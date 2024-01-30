"""Scrape a collection from OpenSea."""

import json
import os

from absl import app
from absl import flags
from absl import logging
import cairosvg
import requests

FLAGS = flags.FLAGS

flags.DEFINE_string('collection', None, 'Collection to scrape')
flags.DEFINE_string('output_dir', None, 'Output directory')
flags.DEFINE_string('api_key', None, 'OpenSea API key')

def get_collection(collection_name):
    """Get collection info from OpenSea API."""
    uri = f'https://api.opensea.io/v2/collection/{collection_name}/nfts'
    response = requests.get(uri, headers={'X-API-KEY': FLAGS.api_key})
    nfts = response.json()['nfts']
    next_token = response.json()['next']
    while next_token:
        response = requests.get(uri,
                                headers={'X-API-KEY': FLAGS.api_key},
                                params={'next': next_token})
        nfts.extend(response.json()['nfts'])
        next_token = response.json().get('next', None)
        logging.info('Total number: %d NFTs', len(nfts))
    return nfts


def save_nft_collection_metadata(nfts):
    """Save NFT collection metadata to a JSON file."""
    with open(os.path.join(FLAGS.output_dir, 'metadata.json'), 'w') as json_file:
        json.dump(nfts, json_file, indent=2)
    logging.info('Saved metadata.json to %s', os.path.join(FLAGS.output_dir, 'metadata.json'))



def main(_):
    if os.path.exists(os.path.join(FLAGS.output_dir, 'metadata.json')):
        nfts = json.load(open(os.path.join(FLAGS.output_dir, 'metadata.json')))
    else:
        nfts = get_collection(FLAGS.collection)
        save_nft_collection_metadata(nfts)
    os.makedirs(FLAGS.output_dir, exist_ok=True)
    for nft in nfts:
        svg_data = requests.get(nft['image_url']).text
        if os.path.exists(os.path.join(FLAGS.output_dir, nft['name'] + '.png')):
            logging.info('Image %s already exists', nft['name'])
            continue
        with open(os.path.join(FLAGS.output_dir, nft['name'] + '.png'),
                  'wb') as png_file:
            cairosvg.svg2png(bytestring=svg_data, write_to=png_file)
            logging.info('Saved %s', nft['name'])


if __name__ == '__main__':
    app.run(main)
