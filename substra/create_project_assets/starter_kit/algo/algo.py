import opener
import argparse


def train(inmodels=None, rank=0):
    # 1. load data using opener.get_X and opener.get_y
    # 2. load pre-existing models
    #    models are stored in the "./model/" folder
    #    the inmodels param is the list of all pre-existing model filenames to use during the training
    # 3. train algorithm and produce new model
    # 4. save new model
    #    new model must be saved under the "./model/" folder under the filename "model" (i.e. "./model/model")
    # 5. save predictions made on train data (opener.get_X) using opener.save_pred
    pass


def predict(inmodels=None):
    # 1. load data using opener.get_X and opener.get_y
    # 2. load a model
    #    the model file name is "model" and is in the "./model/" folder (i.e. "./model/model")
    #    the inmodels param is a list containing a single element: the filename of the model to load
    # 3. save predictions made on train data (opener.get_X) using opener.save_pred
    pass


def dry_run(inmodels=None):
    # 1. load data using opener.fake_X and opener.fake_y
    # 2. load pre-existing models
    #    models are stored in the "./model/" folder
    #    the inmodels param is the list of all pre-existing model filenames to use during the training
    # 3. train algorithm and produce new model
    # 4. save new model
    #    new model must be saved under the "./model/" folder under the filename "model" (i.e. "./model/model")
    # 5. save predictions made on train data (generated at step 1) using opener.save_pred
    pass


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dry-run', action='store_true', default=False,
                        help='Launch dry run')
    parser.add_argument('-t', '--train', action='store_true', default=False,
                        help='Launch train')
    parser.add_argument('-p', '--predict', action='store_true', default=False,
                        help='Launch predict')
    parser.add_argument('-m', '--inmodels', metavar='TraintupleKey', type=str, nargs='*',
                        help='List of models from traintuplekey')
    parser.add_argument('-r', '--rank', type=int, default=0,
                        help='Rank of the fltask, if one')
    args = vars(parser.parse_args())

    logging.info(args)

    if args['train']:
        train(inmodels=args['inmodels'], rank=args['rank'])
    elif args['predict']:
        predict(inmodels=args['inmodels'])
    elif args['dry_run']:
        dry_run(inmodels=args['inmodels'])
    else:
        raise ValueError('task not implemented, should be either train, predict or dry-run')
