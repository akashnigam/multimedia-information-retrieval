import argparse
from Phase2.APIs.generic_apis import *
import numpy as np

np.warnings.filterwarnings('ignore')


def parse_args_process():
    argument_parse = argparse.ArgumentParser()
    argument_parse.add_argument('--file', help='What you want to choose user/image/location?', type=str, required=True,
                                )
    argument_parse.add_argument('--model', help='The model you want to use(PCA/SVD/LDA)', type=str, required=True,
                                choices=['PCA', 'SVD', 'LDA'])
    argument_parse.add_argument('--k', help='The number semantics you want to find', type=int, required=True)
    args = argument_parse.parse_args()
    return args


file_to_read = {
    'user': '../Data/devset_textTermsPerUser.txt',
    'image': '../Data/devset_textTermsPerImage.txt',
    'location': '../Data/devset_textTermsPerPOI.txt'
}
feature_reduce = {
    'PCA': get_PCA,
    'SVD': get_SVD,
    'LDA': get_LDA
}

args = parse_args_process()
vector, columns, rows = tDictionary_to_vector(read_text_descriptor_files(args.file))
vector = normalize_vector(vector)
reduced_vector, latent_semantics = feature_reduce[args.model](vector, args.k)
d = {x: i for i, x in enumerate(rows)}
user_id = reduced_vector[d[input('enter the id')]]
distances = consine_similarity(reduced_vector, user_id)
similarity = return_max_k(distances, 5)
# similarity = list(zip(np.take(np.array(rows), similarity), similarity))
rows = np.array(list(rows))
ans = list(zip(np.take(rows, similarity), np.take(distances, similarity)))
print(ans)
