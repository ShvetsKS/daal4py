#*******************************************************************************
# Copyright 2014-2020 Intel Corporation
# All Rights Reserved.
#
# This software is licensed under the Apache License, Version 2.0 (the
# "License"), the following terms apply:
#
# You may not use this file except in compliance with the License.  You may
# obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#
# See the License for the specific language governing permissions and
# limitations under the License.
#*******************************************************************************

# daal4py Gradient Bossting Classification model creation from XGBoost example

import daal4py as d4p
import xgboost as xgb
import numpy as np
import pandas as pd

def main():
    # Path to data
    train_file = "./data/batch/df_classification_train.csv"
    test_file = "./data/batch/df_classification_test.csv"

    # Data reading
    feature_names = ["feature_" + str(i) for i in range(3)]
    X_train = pd.read_csv(train_file, usecols=range(3), dtype=np.float32, names=feature_names)
    y_train = pd.read_csv(train_file, usecols=range(3, 4), dtype=np.float32, names=["label"])
    X_test = pd.read_csv(test_file, usecols=range(3), dtype=np.float32, names=feature_names)
    y_test = pd.read_csv(test_file, usecols=range(3, 4), dtype=np.float32, names=["label"])

    # Datasets creation
    xgb_train = xgb.DMatrix(X_train, label=y_train)
    xgb_test = xgb.DMatrix(X_test)

    # training parameters setting
    params = {
        'max_bin':          256,
        'scale_pos_weight': 2,
        'lambda_l2':        1,
        'alpha':            0.9,
        'max_depth':        8,
        'num_leaves':       2**8,
        'verbosity':        0,
        'objective':        'multi:softmax',
        'learning_rate':    0.3,
        'num_class':        5,
    }

    # Training
    xgb_model = xgb.train(params, xgb_train, num_boost_round=2)

    # XGBoost prediction
    xgb_prediction = xgb_model.predict(xgb_test)
    xgb_errors_count = np.count_nonzero(xgb_prediction - np.ravel(y_test))

    # Conversion to daal4py
    daal_model = d4p.get_gbt_model_from_xgboost(xgb_model)

    # daal4py prediction
    daal_predict_algo = d4p.gbt_classification_prediction(
        nClasses=5, resultsToEvaluate="computeClassLabels", fptype='float')
    daal_prediction = daal_predict_algo.compute(X_test, daal_model)
    daal_errors_count = np.count_nonzero(daal_prediction.prediction - y_test)
    assert np.absolute(xgb_errors_count - daal_errors_count) == 0

    return (xgb_prediction, xgb_errors_count, np.ravel(daal_prediction.prediction), daal_errors_count, np.ravel(y_test))


if __name__ == "__main__":
    (xgb_prediction, xgb_errors_count, daal_prediction, daal_errors_count, y_test) = main()
    print("\nXGBoost prediction results (first 10 rows):\n", xgb_prediction[0:10])
    print("\ndaal4py prediction results (first 10 rows):\n", daal_prediction[0:10])
    print("\nGround truth (first 10 rows):\n", y_test[0:10])

    print("XGBoost errors count:", xgb_errors_count)
    print("XGBoost accuracy score:", xgb_errors_count/xgb_prediction.shape[0])

    print("\ndaal4py errors count:", daal_errors_count)
    print("daal4py accuracy score:", daal_errors_count/daal_prediction.shape[0])
    print("\nAll looks good!")
