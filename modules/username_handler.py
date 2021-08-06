"""Username Scanner - Based on https://github.com/sherlock-project."""
import json
from configparser import ConfigParser
from typing import Dict, List, Optional, Tuple, Union
from time import monotonic

import logging
import re
import requests

from urllib3.exceptions import InsecureRequestWarning
from requests_futures.sessions import FuturesSession
from core.base_module import BaseModule
from core.resources_manager import ResourcesFileHandler
from core.temp_file import TempFileHandler


logger = logging.getLogger()


class UsernameScanner(BaseModule):
    """Username Handler."""

    QS_CLAIMED = "Claimed"   # Username Detected
    QS_AVAILABLE = "Available"  # Username Not Detected
    QS_UNKNOWN = "Unknown"   # Error Occurred While Trying To Detect Username
    QS_ILLEGAL = "Illegal"   # Username Not Allowable For This Site

    def run(self, config: ConfigParser, args: Dict, data: Dict) -> None:
        """Execute Module."""

        # Suppress only the single warning from urllib3 needed.
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)  # type: ignore

        if 'username' not in data:
            data.update({'username': {'target_username': ''}})

        target_username: str = data['username']['target_username']

        if target_username == '':
            if args['username'] == '':
                logger.info('\t\tUsername Not Provided. Skipping...')
                return

            target_username = args['username']
            data['username']['target_username'] = target_username

        # Load the Targets File
        targets: Dict = json.loads(''.join(ResourcesFileHandler.read_file_text('username_scanner_targets.json')))

        # Check for NSFW Sites
        if args['username_allow_nsfw_scan']:
            logger.info('\t\tNSFW Sites Allowed.')
            targets.update(json.loads(''.join(ResourcesFileHandler.read_file_text('username_scanner_targets_nsfw.json'))))

        # Scan
        target_file: str = f'username_search/{target_username}.json'
        h_result: Optional[Dict] = None

        if not TempFileHandler.file_exist(target_file):
            h_result = self.__do_scan(
                target_username=target_username,
                target_sites=targets,
                config=config,
                args=args
                )
            TempFileHandler.write_file_text(target_file, json.dumps(h_result))
        else:
            logger.info(f'\t\tTarget File "{target_file}". Loading...')
            h_result = json.loads(''.join(TempFileHandler.read_file_text(target_file)))

        # Dump the Output File
        if args['username_enable_dump_file']:
            dump_file_content: str = 'site,url'

            for _key, value in h_result.items():  # type: ignore
                if 'status' in value and value['status']['status'] == UsernameScanner.QS_CLAIMED:
                    dump_file_content += f'\n"{value["status"]["site_name"]}","{value["status"]["site_url_user"]}"'

            with open(f'data/export/username_{target_username}.csv', 'w', encoding='utf-8') as file:
                file.write(dump_file_content)
                file.flush()
                file.close()

    def __do_scan(self, target_username: str, target_sites: Dict, config: ConfigParser, args: Dict) -> Dict:
        """
        Execute the Scan.

        :param target_username:
        :param target_sites:
        :return:
        """

        # Create multi-threaded session for all requests.
        session: FuturesSession = self.__create_session(target_sites=target_sites)

        # Results from analysis of all sites
        results_total: Dict = self.__create_futures(
            target_username=target_username,
            target_sites=target_sites,
            config=config,
            session=session
            )

        # Parse the Results
        self.__parse_data(
            target_username=target_username,
            target_sites=target_sites,
            results_total=results_total,
            args=args
            )

        return results_total

    def __parse_data(self, target_username: str, target_sites: Dict, results_total: Dict, args: Dict) -> None:  # pylint: disable=R0914
        """
        Download and Parse WebSites Data.

        :param target_username:
        :param target_sites:
        :param results_total:
        :param args:
        :return:
        """

        # Open the file containing account links
        # Core logic: If tor requests, make them here. If multi-threaded requests, wait for responses
        for social_network, net_info in target_sites.items():

            # Retrieve results again
            results_site: Dict = results_total[social_network]

            # Retrieve other site information again
            url: str = results_site['url_user']
            status: Optional[str] = results_site['status'] if 'status' in results_site else None
            if status is not None:
                # We have already determined the user doesn't exist here
                continue

            # Get the expected error type
            error_type: str = net_info["errorType"]

            # Retrieve future and ensure it has finished
            future = net_info["request_future"]
            request_future, error_text, _expection_text = self.__get_response(
                request_future=future
                )

            if request_future is None:
                continue

            # Get response time for response of our request.
            response_time: float = float(request_future.elapsed) if request_future is not None else -1.0   # type: ignore
            http_status: int = request_future.status_code if request_future is not None else 0
            response_text: str = request_future.text if request_future is not None else ""

            if error_text is not None and error_text != '':
                result = self.__build(
                    target_username,
                    social_network,
                    url,
                    UsernameScanner.QS_UNKNOWN,
                    query_time=response_time,
                    context=error_text
                    )

            elif error_type == "message":
                result = self.__parse_single_message(net_info, request_future, response_time, social_network, target_username, url)

            elif error_type == "status_code":
                result = self.__parse_by_status_code(request_future, response_time, social_network, target_username, url)

            elif error_type == "response_url":
                result = self.__parse_by_url(request_future, response_time, social_network, target_username, url)

            else:
                # It should be impossible to ever get here...
                raise ValueError(f"Unknown Error Type '{error_type}' for "
                                 f"site '{social_network}'")

            # Save status of request
            results_site['status'] = result

            # Save results from request
            results_site['http_status'] = http_status

            try:
                results_site['response_text'] = response_text
            except:  # pylint: disable=W0702 # noqa: B001, E722, D901
                results_site['response_text'] = ''

            # Add this site's results into final dictionary with all of the other results.
            results_total[social_network] = results_site

            if args['username_print_result']:
                if args['username_show_all'] or (not args['username_show_all'] and result['status'] == UsernameScanner.QS_CLAIMED):
                    logger.info(f'\t\t{social_network}: {result["status"]} > {result["site_url_user"]}')

    def __parse_by_url(self, request_future: requests.Response, response_time: float, social_network: str, target_username: str, url: str) -> Dict:  # pylint: disable=R0913
        """Parse the Result by URL."""

        # For this detection method, we have turned off the redirect.
        # So, there is no need to check the response URL: it will always
        # match the request.  Instead, we will ensure that the response
        # code indicates that the request was successful (i.e. no 404, or
        # forward to some odd redirect).
        if 200 <= request_future.status_code < 300:
            return self.__build(target_username,
                                social_network,
                                url,
                                UsernameScanner.QS_CLAIMED,
                                query_time=response_time
                                )

        return self.__build(target_username,
                            social_network,
                            url,
                            UsernameScanner.QS_AVAILABLE,
                            query_time=response_time
                            )

    def __parse_by_status_code(self, request_future: requests.Response, response_time: float, social_network: str, target_username: str, url: str) -> Dict:  # pylint: disable=R0913
        """Parse the Result by Status Code."""

        # Checks if the status code of the response is 2XX
        if not request_future.status_code >= 300 or request_future.status_code < 200:
            return self.__build(target_username,
                                social_network,
                                url,
                                UsernameScanner.QS_CLAIMED,
                                query_time=response_time
                                )

        return self.__build(target_username,
                            social_network,
                            url,
                            UsernameScanner.QS_AVAILABLE,
                            query_time=response_time
                            )

    def __parse_single_message(self, net_info: Dict, request_future: requests.Response, response_time: float, social_network: str, target_username: str, url: str) -> Dict:  # pylint: disable=R0913
        """Parse the Result by Message."""

        # error_flag True denotes no error fo
        # und in the HTML
        # error_flag False denotes error found in the HTML
        error_flag = True
        errors: Union[str, List] = net_info['errorMsg']
        # errors will hold the error message
        # it can be string or list
        # by insinstance method we can detect that
        # and handle the case for strings as normal procedure
        # and if its list we can iterate the errors
        if isinstance(errors, str):
            # Checks if the error message is in the HTML
            # if error is present we will set flag to False
            if errors in request_future.text:
                error_flag = False
        else:
            # If it's list, it will iterate all the error message
            for error in errors:
                if error in request_future.text:
                    error_flag = False
                    break

        if error_flag:
            return self.__build(target_username,
                                social_network,
                                url,
                                UsernameScanner.QS_CLAIMED,
                                query_time=response_time
                                )

        return self.__build(target_username,
                            social_network,
                            url,
                            UsernameScanner.QS_AVAILABLE,
                            query_time=response_time
                            )

    def __create_futures(self, target_username: str, target_sites: Dict, config: ConfigParser, session: FuturesSession) -> Dict:
        """Create the Request Futures."""

        # Results from analysis of all sites
        results_total: Dict = {}

        # First create futures for all requests. This allows for the requests to run in parallel
        for social_network, net_info in target_sites.items():

            # Results from analysis of this specific site
            results_site: Dict = {}

            # Record URL of main site
            results_site['url_main'] = net_info.get("urlMain")

            # A user agent is needed because some sites don't return the correct
            # information since they think that we are bots (Which we actually are...)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0',
                }

            if "headers" in net_info:
                # Override/append any extra headers required by a given site.
                headers.update(net_info["headers"])

            # URL of user on site (if it exists)
            url = net_info["url"].format(target_username)

            # Don't make request if username is invalid for the site
            regex_check = net_info.get("regexCheck")
            if regex_check and re.search(regex_check, target_username) is None:
                # No need to do the check at the site: this user name is not allowed.
                results_site['status'] = self.__build(target_username,
                                                      social_network,
                                                      url,
                                                      UsernameScanner.QS_ILLEGAL)
                results_site["url_user"] = ""
                results_site['http_status'] = ""
                results_site['response_text'] = ""

            else:
                # URL of user on site (if it exists)
                results_site["url_user"] = url
                url_probe = net_info.get("urlProbe")
                if url_probe is None:
                    # Probe URL is normal one seen by people out on the web.
                    url_probe = url
                else:
                    # There is a special URL for probing existence separate
                    # from where the user profile normally can be found.
                    url_probe = url_probe.format(target_username)

                if (net_info["errorType"] == 'status_code' and net_info.get("request_head_only", True)):
                    # In most cases when we are detecting by status code,
                    # it is not necessary to get the entire body:  we can
                    # detect fine with just the HEAD response.
                    request_method = session.head
                else:
                    # Either this detect method needs the content associated
                    # with the GET response, or this specific website will
                    # not respond properly unless we request the whole page.
                    request_method = session.get

                if net_info["errorType"] == "response_url":
                    # Site forwards request to a different URL if username not
                    # found.  Disallow the redirect so we can capture the
                    # http status from the original URL request.
                    allow_redirects = False
                else:
                    # Allow whatever redirect that the site wants to do.
                    # The final result of the request will be what is available.
                    allow_redirects = True

                # This future starts running the request in a new thread, doesn't block the main thread
                future = request_method(url=url_probe, headers=headers,
                                        allow_redirects=allow_redirects,
                                        timeout=int(config['MODULE_UsernameScanner']['connection_timeout_sec'])
                                        )

                # Store future in data for access later
                net_info["request_future"] = future

            # Add this site's results into final dictionary with all of the other results.
            results_total[social_network] = results_site

        return results_total

    def __create_session(self, target_sites: Dict) -> FuturesSession:
        """Create the HTTP Session."""

        # Normal requests
        underlying_session = requests.session()
        underlying_session.verify = False

        # Limit number of workers to 20.
        if len(target_sites) >= 20:
            max_workers = 20
        else:
            max_workers = len(target_sites)

        logger.info(f'\t\tStarting Scan with {max_workers} Workers.')

        # Create multi-threaded session for all requests.
        return SherlockFuturesSession(
            max_workers=max_workers,
            session=underlying_session
            )

    def __get_response(self, request_future: FuturesSession) -> Tuple[Optional[requests.Response], str, str]:

        # Default for Response object if some failure occurs.
        response: Optional[requests.Response] = None

        error_context: str = 'General Unknown Error'
        expected_text: str = ''

        try:
            response = request_future.result()
            if response is not None and response.status_code:
                error_context = ''

        except requests.exceptions.HTTPError as errh:
            error_context = "HTTP Error"
            expected_text = str(errh)

        except requests.exceptions.ProxyError as errp:
            error_context = "Proxy Error"
            expected_text = str(errp)

        except requests.exceptions.ConnectionError as errc:
            error_context = "Error Connecting"
            expected_text = str(errc)

        except requests.exceptions.Timeout as errt:
            error_context = "Timeout Error"
            expected_text = str(errt)

        except requests.exceptions.RequestException as err:
            error_context = "Unknown Error"
            expected_text = str(err)

        return response, error_context, expected_text

    def __build(self, username: str, site_name: str, site_url_user: str, status: str, query_time: Optional[float] = None, context: str = None) -> Dict:  # pylint: disable=R0913
        """
        Create Query Result Object.

        Contains information about a specific method of detecting usernames on
        a given type of web sites.

        :param username: String indicating username that query result was about
        :param site_name: String which identifies site
        :param site_url_user: String containing URL for username on site
        :param status: Indicate the status of the query
        :param query_time: Time (in seconds) required to perform query
        :param context: String indicating any additional context about the query.  For example, if there was an error, this might indicate the type of error that occurred
        :return:
        """

        return {
            'username': username,
            'site_name': site_name,
            'site_url_user': site_url_user,
            'status': status,
            'query_time': query_time,
            'context': context
            }


class SherlockFuturesSession(FuturesSession):  # type: ignore
    """Sherlock Future Session."""

    def request(self, method, url, hooks={}, *args, **kwargs):  # type: ignore # pylint: disable=R0913, W1113, W0102 # noqa: B006
        """
        Request.

        This extends the FuturesSession request method to calculate a response
        time metric to each request.
        It is taken (almost) directly from the following StackOverflow answer:
        https://github.com/ross/requests-futures#working-in-the-background

        :param method: String containing method desired for request.
        :param url: String containing URL for request.
        :param hooks: Dictionary containing hooks to execute after request finishes.
        :param args: Arguments.
        :param kwargs: Keyword arguments.
        :return:
        """

        # Record the start time for the request.
        start = monotonic()

        def response_time(resp, *args, **kwargs):  # type: ignore # pylint:disable=W0613
            """Response Time Hook."""

            resp.elapsed = monotonic() - start

            return resp

        # Install hook to execute when response completes.
        # Make sure that the time measurement hook is first, so we will not
        # track any later hook's execution time.
        try:
            if isinstance(hooks['response'], list):
                hooks['response'].insert(0, response_time)
            elif isinstance(hooks['response'], tuple):
                # Convert tuple to list and insert time measurement hook first.
                hooks['response'] = list(hooks['response'])
                hooks['response'].insert(0, response_time)  # type: ignore
            else:
                # Must have previously contained a single hook function,
                # so convert to list.
                hooks['response'] = [response_time, hooks['response']]
        except KeyError:
            # No response hook was already defined, so install it ourselves.
            hooks['response'] = [response_time]

        return super(SherlockFuturesSession, self).request(method, url, hooks=hooks, *args, **kwargs)  # pylint: disable=R1725
