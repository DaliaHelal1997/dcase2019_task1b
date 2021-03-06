import numpy as np
from scipy.special import softmax
from pathlib import Path
from sklearn.preprocessing import LabelEncoder
import sys

models_ = sys.argv[1:]

assert len(models_) > 0

for create_for in ['test', 'submission']:
    nr_folds = 4
    id = 'models_[' + '_and_'.join(models_) +']'

    le = LabelEncoder().fit(['airport',
                             'bus',
                             'metro',
                             'metro_station',
                             'park',
                             'public_square',
                             'shopping_mall',
                             'street_pedestrian',
                             'street_traffic',
                             'tram'])
    files = []
    for m in models_:
        p = Path('.').glob('./data/tmp/{}/*{}_best.npy'.format(m, create_for))
        f = [x for x in sorted(p) if x.is_file()]
        if len(f) != 4:
            print(m)
            assert False
        files.append(f)
    print('# nr models: {}'.format(len(files)))

    predictions = []

    for i, model in enumerate(files):
        for file in model:
            predictions.append(softmax(np.load(file), axis=1))

    prediction = np.mean(predictions, axis=0)

    filenames = np.load(Path('./data/tmp/{}_filenames.npy'.format(create_for)))
    print('# samples to predict: {}'.format(len(filenames)))

    if create_for == 'test':
        csv = [('Id', 'Scene_label')]
        delimiter = ','
        filename_ = '{}'

    elif create_for == 'submission':
        csv = []
        delimiter = '\t'
        filename_ = 'audio/{}.wav'

    prediction = np.argmax(prediction, axis=1)
    for name, label in zip(filenames, le.inverse_transform(prediction)):
        csv.append((filename_.format(name.split('/')[-1]), label))

    np.savetxt(
        Path('./data/tmp/predictions_' + id + '_'+  create_for + '.csv'),
        csv,
        delimiter=delimiter,
        fmt="%s"
    )
    print('# length of csv: {}'.format(len(csv)))
