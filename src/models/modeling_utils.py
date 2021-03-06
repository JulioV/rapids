import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler, RobustScaler
from imblearn.over_sampling import SMOTE
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, classification_report, confusion_matrix
from sklearn.metrics import precision_recall_fscore_support
from sklearn.metrics import cohen_kappa_score, roc_auc_score
from imblearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE

# drop columns with zero variance
def dropZeroVarianceCols(data):
    if not data.empty:
        var_df = data.var()
        keep_col = []
        for col in var_df.index:
            if var_df.loc[col] > 0:
                keep_col.append(col)
        data_drop_cols_var = data.loc[:, keep_col]
    else:
        data_drop_cols_var = data
    return data_drop_cols_var

# normalize based on all participants: return fitted scaler
def getNormAllParticipantsScaler(features, scaler_flag):
    # MinMaxScaler
    if scaler_flag == "minmaxscaler":
        scaler = MinMaxScaler()
    # StandardScaler
    elif scaler_flag == "standardscaler":
        scaler = StandardScaler()
    # RobustScaler
    elif scaler_flag == "robustscaler":
        scaler = RobustScaler()
    else:
        # throw exception
        raise ValueError("The normalization method is not predefined, please check if the PARAMS_FOR_ANALYSIS.NORMALIZED in config.yaml file is correct.")
    scaler.fit(features)
    return scaler

# get metrics: accuracy, precision1, recall1, f11, auc, kappa
def getMetrics(pred_y, pred_y_prob, true_y):
    acc = accuracy_score(true_y, pred_y)
    pre1 = precision_score(true_y, pred_y, average=None, labels=[0,1])[1]
    recall1 = recall_score(true_y, pred_y, average=None, labels=[0,1])[1]
    f11 = f1_score(true_y, pred_y, average=None, labels=[0,1])[1]
    auc = roc_auc_score(true_y, pred_y_prob)
    kappa = cohen_kappa_score(true_y, pred_y)

    return acc, pre1, recall1, f11, auc, kappa

# get feature importances
def getFeatureImportances(model, clf, cols):
    if model == "LogReg":
        # Extract the coefficient of the features in the decision function
        # Calculate the absolute value
        # Normalize it to sum 1
        feature_importances = pd.DataFrame(zip(clf.coef_[0],cols), columns=["Value", "Feature"])
        feature_importances["Value"] = feature_importances["Value"].abs()/feature_importances["Value"].abs().sum()
    elif model == "kNN":
        # Feature importance is not defined for the KNN Classification, return an empty dataframe
        feature_importances = pd.DataFrame(columns=["Value", "Feature"])
    elif model == "SVM":
        # Coefficient of the features are only available for linear kernel
        try:
            # For linear kernel
            # Extract the coefficient of the features in the decision function
            # Calculate the absolute value
            # Normalize it to sum 1
            feature_importances = pd.DataFrame(zip(clf.coef_[0],cols), columns=["Value", "Feature"])
            feature_importances["Value"] = feature_importances["Value"].abs()/feature_importances["Value"].abs().sum()
        except:
            # For nonlinear kernel, return an empty dataframe directly
            feature_importances = pd.DataFrame(columns=["Value", "Feature"])
    elif model == "LightGBM":
        # Extract feature_importances_ and normalize it to sum 1
        feature_importances = pd.DataFrame(zip(clf.feature_importances_,cols), columns=["Value", "Feature"])
        feature_importances["Value"] = feature_importances["Value"]/feature_importances["Value"].sum()
    else:
        # For DT, RF, GB, XGBoost classifier, extract feature_importances_. This field has already been normalized.
        feature_importances = pd.DataFrame(zip(clf.feature_importances_,cols), columns=["Value", "Feature"])

    feature_importances = feature_importances.set_index(["Feature"]).T

    return feature_importances

def createPipeline(model):
    if model == "LogReg":
        from sklearn.linear_model import LogisticRegression
        pipeline = Pipeline([
            ("sampling", SMOTE(sampling_strategy="minority", random_state=0)),
            ("clf", LogisticRegression(random_state=0))
        ])
    elif model == "kNN":
        from sklearn.neighbors import KNeighborsClassifier
        pipeline = Pipeline([
            ("sampling", SMOTE(sampling_strategy="minority", random_state=0)),
            ("clf", KNeighborsClassifier())
        ])
    elif model == "SVM":
        from sklearn.svm import SVC
        pipeline = Pipeline([
            ("sampling", SMOTE(sampling_strategy="minority", random_state=0)),
            ("clf", SVC(random_state=0, probability=True))
        ])
    elif model == "DT":
        from sklearn.tree import DecisionTreeClassifier
        pipeline = Pipeline([
            ("sampling", SMOTE(sampling_strategy="minority", random_state=0)),
            ("clf", DecisionTreeClassifier(random_state=0))
        ])
    elif model == "RF":
        from sklearn.ensemble import RandomForestClassifier
        pipeline = Pipeline([
            ("sampling", SMOTE(sampling_strategy="minority", random_state=0)),
            ("clf", RandomForestClassifier(random_state=0))
        ])
    elif model == "GB":
        from sklearn.ensemble import GradientBoostingClassifier
        pipeline = Pipeline([
            ("sampling", SMOTE(sampling_strategy="minority", random_state=0)),
            ("clf", GradientBoostingClassifier(random_state=0))
        ])
    elif model == "XGBoost":
        from xgboost import XGBClassifier
        pipeline = Pipeline([
            ("sampling", SMOTE(sampling_strategy="minority", random_state=0)),
            ("clf", XGBClassifier(random_state=0))
        ])
    elif model == "LightGBM":
        from lightgbm import LGBMClassifier
        pipeline = Pipeline([
            ("sampling", SMOTE(sampling_strategy="minority", random_state=0)),
            ("clf", LGBMClassifier(random_state=0))
        ])
    else:
        raise ValueError("RAPIDS pipeline only support LogReg, kNN, SVM, DT, RF, GB, XGBoost, and LightGBM algorithms for classification problems.")

    return pipeline
