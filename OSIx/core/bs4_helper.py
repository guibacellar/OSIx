"""Helper to Operate Safely BS4."""

from typing import Optional, Tuple, Union
from bs4 import BeautifulSoup, ResultSet, Tag


class BS4Helper:
    """Helper to Operate Safely BS4."""

    def __init__(self, soup: BeautifulSoup):
        """Initialize the BS4Helper."""
        self.soup = soup

    def find_by_attribute(self, attribute_data: Tuple[str, str], target_index: int, target_property: str, null_value: Optional[str] = None, target: Optional[Union[ResultSet, Tag]] = None) -> Optional[str]:
        """Safely find Value by Attribute."""

        attr: ResultSet = self.soup.findAll(attrs={attribute_data[0]: attribute_data[1]}) if target is None else target.findAll(attrs={attribute_data[0]: attribute_data[1]})

        if attr is None or len(attr) <= 0 or len(attr) < (target_index - 1):
            return null_value

        target_tag: Tag = attr[target_index]

        if target_property == 'string':
            return self.clenup_string(target_tag.string)

        if target_property == 'text':
            return self.clenup_string(target_tag.text)

        return self.clenup_string(target_tag.attrs[target_property])

    def clenup_string(self, content: Optional[str]) -> Optional[str]:
        """Cleanup the Strings."""

        if content is None:
            return None

        h_result: str = str(content.replace('\n', ''))

        while '  ' in h_result:
            h_result = h_result.replace('  ', ' ')

        return h_result.rstrip().lstrip()
