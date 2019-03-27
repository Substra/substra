import json
import metrics
import opener


def calc_perf(folder_true="./data", folder_pred="./pred"):
    """compute performances using the imported metrics.score function"""
    # get true and pred values
    y_true = opener.get_y(folder_true)
    y_pred = opener.get_pred(folder_pred)
    return {'all': metrics.score(y_true, y_pred)}


if __name__ == "__main__":
    perf = calc_perf()
    with open('./pred/perf.json', 'w') as outfile:
        json.dump(perf, outfile)
