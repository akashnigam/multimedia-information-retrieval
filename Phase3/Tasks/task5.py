import argparse
from os import listdir
from collections import defaultdict
import numpy as np

np.random.seed(50)


def validate_data():
    location = '../Data/img'
    dictionary = defaultdict(lambda: defaultdict(lambda: set()))
    temp = defaultdict(lambda: set())
    names = set()
    files = set()
    image_names = set()
    for x in listdir(location):
        name, file = x.split()
        names.add(name)
        files.add(file)
        with open('{0}/{1}'.format(location, x), 'r') as f:
            line = f.readline()
            while line:
                data = line.split(',')
                image_name = data[0]
                temp[name].add(image_name)
                if image_name not in dictionary[name][file]:
                    dictionary[name][file].add(image_name)
                    image_names.add(image_name)
                else:
                    raise LookupError('Repitative image_names')
                line = f.readline()

    for x in dictionary:
        for y in dictionary[x]:
            if temp[x] != dictionary[x][y]:
                raise LookupError('The images are mismatched')
    original_names = sorted(list(image_names))
    image_names = {x: i for i, x in enumerate(original_names)}
    names = sorted(list(names))
    files = sorted(list(files))
    ans = [[] for _ in range(len(image_names))]

    for x in names:
        for y in files:
            file_to_read = '{0}/{1} {2}'.format(location, x, y)
            with open(file_to_read, 'r') as f:
                line = f.readline()
                while line:
                    data = line.split(',')
                    image_name = data[0]
                    if len(ans[image_names[image_name]]) < 945:
                        ans[image_names[image_name]] = ans[image_names[image_name]] + list(
                            map(lambda x: float(x), data[1:]))
                    line = f.readline()
    ans = np.array(ans)

    return ans, image_names, original_names


class HashTable:
    def __init__(self, number_hashes, hash_size, input_dimensions):
        self.hash_size = hash_size
        self.input_dimensions = input_dimensions
        self.number_hashes = number_hashes
        self.hashes = []
        self.hashes_dict = []
        for i in range(number_hashes):
            self.hashes.append(np.random.randn(hash_size, input_dimensions))
            self.hashes_dict.append(defaultdict(lambda: set()))

    def generate_hash(self, input_vector):
        ans = []
        for i in range(self.number_hashes):
            temp = (np.matmul(self.hashes[i], input_vector.T).T > 0).astype('int')
            temp = temp.tolist()
            for j in range(len(temp)):
                temp[j] = ''.join(str(x) for x in temp[j])
            ans.append(temp)
        return ans

    def set_item(self, input_vectors, label):
        hashes = self.generate_hash(input_vectors)

        for i in range(self.number_hashes):
            for j in range(len(input_vectors)):
                self.hashes_dict[i][hashes[i][j]].add(j)

    def get_item(self, input_vectors):
        hashes = self.generate_hash(input_vectors)
        ans_set = set()
        for i in range(self.number_hashes):
            for j in range(len(input_vectors)):
                ans_set = ans_set | self.hashes_dict[i][hashes[i][j]]
        return ans_set


def euclidean_dst(vector, original_vector):
    return np.sum((vector - original_vector) ** 2, axis=1) ** 0.5


if __name__ == '__main__':
    k = 3
    similarity_with = '2482756687'
    t = 5
    l = 4
    ans, image_names, names_sorted = validate_data()
    layers = []
    for _ in range(t):
        hash_table = HashTable(2, 40, ans.shape[1])
        hash_table.set_item(ans, names_sorted)
        layers.append(hash_table)

    similarity_indexes = set()
    vector = ans[image_names[similarity_with]].reshape(1, ans.shape[1])
    for i in range(t):
        temp = layers[i].get_item(vector)
        similarity_indexes = similarity_indexes | temp

    vectors = np.take(ans, list(similarity_indexes), axis=0)
    labels = np.take(names_sorted, list(similarity_indexes))
    dst = euclidean_dst(vectors, vector)
    ans = np.argpartition(dst, t)[:t]
    ans_labels = np.take(labels, ans)
    ans_distance = np.take(dst, ans)
    print(ans_labels)
    print(ans_distance)
