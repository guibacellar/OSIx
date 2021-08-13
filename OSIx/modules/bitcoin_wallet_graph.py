"""Bitcoin Wallet Graph Generator."""

import os
from configparser import ConfigParser
from typing import Dict, List

import json
import logging
import time

import networkx as nx

from OSIx.core.base_module import BaseModule
from OSIx.core.temp_file import TempFileHandler

logger = logging.getLogger()


class BitcoinWalletGraphGenerator(BaseModule):
    """Bitcoint Wallet Graph Generator."""

    def run(self, config: ConfigParser, args: Dict, data: Dict) -> None:
        """Execute Module."""

        target_wallet: str = data['bitcoin']['target_wallet']
        target_file: str = f'bitcoin_wallet/{target_wallet}_transactions.json'

        if target_wallet is None or target_wallet == '':
            logger.info('\t\tTarget BTC Wallet Empty.')
            return

        # Check if Cached File Exists
        if not TempFileHandler.file_exist(target_file):
            logger.info(f'\t\tTarget File "{target_file}" Do not Exists. Skipping...')
            return

        logger.info('\t\tGenerating BTC Graph')

        # Load File
        json_data: Dict = json.loads(''.join(TempFileHandler.read_file_text(target_file)))

        # Execute Module
        self.__execute(
            target_wallet=target_wallet,
            json_data=json_data,
            args=args
            )

    def __execute(self, target_wallet: str, json_data: Dict, args: Dict) -> None:
        """
        Execute the Graph Engine.

        :param target_wallet:
        :param target_file:
        :param json_data:
        :return:
        """

        # Initialize Graph Engine
        all_graph: nx.Graph = nx.DiGraph()
        in_graph: nx.Graph = nx.DiGraph()
        out_graph: nx.Graph = nx.DiGraph()

        all_graph.add_node(target_wallet, weight=2)
        in_graph.add_node(target_wallet, weight=2)
        out_graph.add_node(target_wallet, weight=2)

        # Generate Nodes Graph Nodes List
        all_input_nodes: List = []
        all_output_nodes: List = []
        for single_trans in json_data['transactions']:

            # Process Input
            inputs: List = single_trans['inputs']

            for single_input in inputs:
                if 'prev_out' in single_input and single_input['prev_out']['addr'] not in all_input_nodes:
                    all_input_nodes.append(single_input['prev_out']['addr'])

            # Process Output
            outputs: List = single_trans['out']

            for single_output in outputs:
                if single_output['addr'] not in all_output_nodes:
                    all_output_nodes.append(single_output['addr'])

        # Process Input Nodes
        for in_node in all_input_nodes:
            all_graph.add_node(in_node)
            all_graph.add_edge(in_node, target_wallet, key=int(time.clock() * 1000000))

            in_graph.add_node(in_node)
            in_graph.add_edge(in_node, target_wallet, key=int(time.clock() * 1000000))

        # Process Output Nodes
        for out_node in all_output_nodes:
            all_graph.add_node(out_node)
            all_graph.add_edge(target_wallet, out_node, key=int(time.clock() * 1000000))

            out_graph.add_node(out_node)
            out_graph.add_edge(target_wallet, out_node, key=int(time.clock() * 1000000))

        # Set Node Properties
        if args['export_btc_transactions_as_gephi']:
            all_graph.nodes[target_wallet]['viz'] = {'color': {'r': 255, 'g': 0, 'b': 0, 'a': 0}}
            out_graph.nodes[target_wallet]['viz'] = {'color': {'r': 255, 'g': 0, 'b': 0, 'a': 0}}
            in_graph.nodes[target_wallet]['viz'] = {'color': {'r': 255, 'g': 0, 'b': 0, 'a': 0}}

            nx.readwrite.write_gexf(all_graph, f'data/export/btc_wallet_all_{target_wallet}.gexf')
            nx.readwrite.write_gexf(out_graph, f'data/export/btc_wallet_outputs_{target_wallet}.gexf')
            nx.readwrite.write_gexf(in_graph, f'data/export/btc_wallet_inputs_{target_wallet}.gexf')

        elif args['export_btc_transactions_as_graphml']:
            nx.readwrite.write_graphml_xml(all_graph, f'data/export/btc_wallet_all_{target_wallet}.graphml')
            nx.readwrite.write_graphml_xml(out_graph, f'data/export/btc_wallet_outputs_{target_wallet}.graphml')
            nx.readwrite.write_graphml_xml(in_graph, f'data/export/btc_wallet_inputs_{target_wallet}.graphml')

        # Log
        logger.info(f'\t\t3 Exported Files at {os.path.abspath("data/export")}')
