Python files in this directory are for taking the sim output and creating
surrogate models.
================================================================================
| DataSet           | wraps a pd.DataFrame with easy access to factors, predic-|
|                   | tors, estimators, and performance metrics.               |
|-------------------|----------------------------------------------------------|
| MLbase            | extends BaseClass and modifies it to apply more directly |
|                   | to regression and machine learning models.               |
|-------------------|----------------------------------------------------------|
| LogisticRegression| simple classification model for 3-outcome classification |
|                   | (hopefully someday).                                     |
|-------------------|----------------------------------------------------------|
| RFclassification  | random forest model with classification trees. will      |
|                   | complete a grid search, exploring stopping criteria that |
|                   | results in the model that will make best predictions (at |
|                   | least from the hyperparmeters sampled).                  |
================================================================================
