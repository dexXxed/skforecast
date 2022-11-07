################################################################################
#                                 utils                                        #
#                                                                              #
# This work by Joaquin Amat Rodrigo and Javier Escobar Ortiz is licensed       #
# under a Creative Commons Attribution 4.0 International License.              #
################################################################################
# coding=utf-8

from typing import Union, Any, Optional
import warnings
import joblib
import numpy as np
import pandas as pd
import sklearn


def generate_lags_ndarray(
    forecaster_type,
    lags: Any
) -> None:
    """
    Check lags argument input and generate the corresponding numpy ndarray.
    
    Parameters
    ----------
    forecaster_type : ForecasterAutoreg, ForecasterAutoregCustom, 
    ForecasterAutoregDirect, ForecasterAutoregMultiSeries, ForecasterAutoregMultiVariate
        Forcaster type.

    lags : Any
        Lags used as predictors.
        
    Returns
    ----------
    lags : numpy ndarray
        Lags used as predictors.
    
    """

    if isinstance(lags, int) and lags < 1:
        raise ValueError('Minimum value of lags allowed is 1.')

    if isinstance(lags, (list, np.ndarray)):
        for lag in lags:
            if not isinstance(lag, (int, np.int64, np.int32)):
                raise TypeError('All values in `lags` must be int.')
        
    if isinstance(lags, (list, range, np.ndarray)) and min(lags) < 1:
        raise ValueError('Minimum value of lags allowed is 1.')

    if isinstance(lags, int):
        lags = np.arange(lags) + 1
    elif isinstance(lags, (list, range)):
        lags = np.array(lags)
    elif isinstance(lags, np.ndarray):
        lags = lags
    else:
        if not str(forecaster_type).split('.')[1] == 'ForecasterAutoregMultiVariate':
            raise TypeError(
                '`lags` argument must be an int, 1d numpy ndarray, range or list. '
                f"Got {type(lags)}."
            )
        else:
            raise TypeError(
                '`lags` argument must be a dict, int, 1d numpy ndarray, range or list. '
                f"Got {type(lags)}."
            )

    return lags


def check_y(
    y: Any
) -> None:
    """
    Raise Exception if `y` is not pandas Series or if it has missing values.
    
    Parameters
    ----------        
    y : Any
        Time series values.
        
    Returns
    ----------
    None
    
    """
    
    if not isinstance(y, pd.Series):
        raise TypeError('`y` must be a pandas Series.')
        
    if y.isnull().any():
        raise ValueError('`y` has missing values.')
    
    return
    
    
def check_exog(
    exog: Any
) -> None:
    """
    Raise Exception if `exog` is not pandas Series or pandas DataFrame, or
    if it has missing values.
    
    Parameters
    ----------        
    exog :  Any
        Exogenous variable/s included as predictor/s.

    Returns
    ----------
    None

    """
        
    if not isinstance(exog, (pd.Series, pd.DataFrame)):
        raise TypeError('`exog` must be `pd.Series` or `pd.DataFrame`.')

    if exog.isnull().any().any():
        raise ValueError('`exog` has missing values.')
                
    return


def _check_interval(
    interval: list
) -> None:
    """
    Check provided confidence interval sequence is valid.

    Parameters
    ----------
    interval : list, default `None`
        Confidence of the prediction interval estimated. Sequence of percentiles
        to compute, which must be between 0 and 100 inclusive. For example, 
        interval of 95% should be as `interval = [2.5, 97.5]`.
    
    """

    if not isinstance(interval, list):
        raise TypeError(
            ('`interval` must be a `list`. For example, interval of 95% '
             'should be as `interval = [2.5, 97.5]`.')
        )

    if len(interval) != 2:
        raise ValueError(
            ('`interval` must contain exactly 2 values, respectively the '
             'lower and upper interval bounds. For example, interval of 95% '
             'should be as `interval = [2.5, 97.5]`.')
        )

    if (interval[0] < 0.) or (interval[0] >= 100.):
        raise ValueError(
            f'Lower interval bound ({interval[0]}) must be >= 0 and < 100.'
        )

    if (interval[1] <= 0.) or (interval[1] > 100.):
        raise ValueError(
            f'Upper interval bound ({interval[1]}) must be > 0 and <= 100.'
        )

    if interval[0] >= interval[1]:
        raise ValueError(
            f'Lower interval bound ({interval[0]}) must be less than the '
            f'upper interval bound ({interval[1]}).'
        )

    return


def check_predict_input(
    forecaster_type,
    steps: int,
    fitted: bool,
    included_exog: bool,
    index_type: type,
    index_freq: str,
    window_size: int,
    last_window: Union[pd.Series, pd.DataFrame]=None,
    exog: Union[pd.Series, pd.DataFrame]=None,
    exog_type: Union[type, None]=None,
    exog_col_names: Union[list, None]=None,
    interval: list=None,
    max_steps: int=None,
    levels: Optional[Union[str, list]]=None,
    series_levels: list=None
) -> None:
    """
    Check all inputs of predict method. This is a helper function to validate
    that inputs used in predict method match attributes of a forecaster already
    trained.

    Parameters
    ----------
    forecaster_type : ForecasterAutoreg, ForecasterAutoregCustom, 
    ForecasterAutoregDirect, ForecasterAutoregMultiSeries, ForecasterAutoregMultiVariate
        Forcaster type.

    steps : int
        Number of future steps predicted.

    fitted: Bool
        Tag to identify if the regressor has been fitted (trained).

    included_exog : bool
        If the forecaster has been trained using exogenous variable/s.

    index_type : type
        Type of index of the input used in training.

    index_freq : str
        Frequency of Index of the input used in training.

    window_size: int
        Size of the window needed to create the predictors. It is equal to
        `max_lag`.

    last_window : pandas Series, pandas DataFrame, default `None`
        Values of the series used to create the predictors (lags) need in the 
        first iteration of prediction (t + 1).

    exog : pandas Series, pandas DataFrame, default `None`
        Exogenous variable/s included as predictor/s.

    exog_type : type, default `None`
        Type of exogenous variable/s used in training.
        
    exog_col_names : list, default `None`
        Names of columns of `exog` if `exog` used in training was a pandas
        DataFrame.

    interval : list, default `None`
        Confidence of the prediction interval estimated. Sequence of percentiles
        to compute, which must be between 0 and 100 inclusive. For example, 
        interval of 95% should be as `interval = [2.5, 97.5]`.

    max_steps: int, default `None`
        Maximum number of steps allowed (`ForecasterAutoregDirect` and 
        `ForecasterAutoregMultiVariate`).
            
    levels : str, list, default `None`
        Time series to be predicted (`ForecasterAutoregMultiSeries`).

    series_levels : list, default `None`
        Names of the columns (levels) that can be predicted.
    
    """

    if not fitted:
        raise sklearn.exceptions.NotFittedError(
            ('This Forecaster instance is not fitted yet. Call `fit` with '
             'appropriate arguments before using predict.')
        )
    
    if isinstance(steps, int) and steps < 1:
        raise ValueError(
            f'`steps` must be an integer greater than or equal to 1. Got {steps}.'
        )

    if isinstance(steps, list) and min(steps) < 0:
        raise ValueError(
           (f"The minimum value of `steps` must be equal to or greater than 1. "
            f"Got {min(steps) + 1}.")
        )

    if max_steps is not None:
        if max(steps)+1 > max_steps:
            raise ValueError(
                (f"The maximum value of `steps` must be less than or equal to "
                 f"the value of steps defined when initializing the forecaster. "
                 f"Got {max(steps)+1}, but the maximum is {max_steps}.")
            )

    if interval is not None:
        _check_interval(interval = interval)
    
    if str(forecaster_type).split('.')[1] == 'ForecasterAutoregMultiSeries':
        if levels is not None and not isinstance(levels, (str, list)):
            raise TypeError(
                f'`levels` must be a `list` of column names, a `str` of a column name or `None`.'
            )

        if len(set(levels) - set(series_levels)) != 0:
            raise ValueError(
                f'`levels` must be in `series_levels` : {series_levels}.'
            )

    if exog is None and included_exog:
        raise ValueError(
            ('Forecaster trained with exogenous variable/s. '
             'Same variable/s must be provided in `predict()`.')
        )
        
    if exog is not None and not included_exog:
        raise ValueError(
            ('Forecaster trained without exogenous variable/s. '
             '`exog` must be `None` in `predict()`.')
        )
    
    if exog is not None:
        max_step = max(steps)+1 if isinstance(steps, list) else steps
        if len(exog) < max_step:
            raise ValueError(
                f'`exog` must have at least as many values as the distance to '
                f'the maximum step predicted, {max_step}.'
            )
        if not isinstance(exog, (pd.Series, pd.DataFrame)):
            raise TypeError('`exog` must be a pandas Series or DataFrame.')
        if exog.isnull().values.any():
            raise ValueError('`exog` has missing values.')
        if not isinstance(exog, exog_type):
            raise TypeError(
                f'Expected type for `exog`: {exog_type}. Got {type(exog)}.'     
            )
        if isinstance(exog, pd.DataFrame):
            col_missing = set(exog_col_names).difference(set(exog.columns))
            if col_missing:
                raise ValueError(
                    (f'Missing columns in `exog`. Expected {exog_col_names}. '
                     f'Got {exog.columns.to_list()}.') 
                )
        check_exog(exog = exog)
        _, exog_index = preprocess_exog(exog=exog.iloc[:0, ])
        
        if not isinstance(exog_index, index_type):
            raise TypeError(
                (f'Expected index of type {index_type} for `exog`. '
                 f'Got {type(exog_index)}.')
            )
        
        if isinstance(exog_index, pd.DatetimeIndex):
            if not exog_index.freqstr == index_freq:
                raise TypeError(
                    (f'Expected frequency of type {index_freq} for `exog`. '
                     f'Got {exog_index.freqstr}.')
                )
        
    if last_window is not None:
        if len(last_window) < window_size:
            raise ValueError(
                (f'`last_window` must have as many values as as needed to '
                 f'calculate the predictors. For this forecaster it is {window_size}.')
            )
                
        if str(forecaster_type).split('.')[1] in \
           ['ForecasterAutoregMultiSeries', 'ForecasterAutoregMultiVariate']:
            if not isinstance(last_window, pd.DataFrame):
                raise TypeError(
                    f'`last_window` must be a pandas DataFrame. Got {type(last_window)}.'
                )
            
            if (str(forecaster_type).split('.')[1] == 'ForecasterAutoregMultiSeries') and \
               (len(set(levels) - set(last_window.columns)) != 0):
                raise ValueError(
                    (f'`last_window` must contain a column(s) named as the level(s) to be predicted.\n'
                     f'    `levels` : {levels}.\n'
                     f'    `last_window` columns : {list(last_window.columns)}.')
                )
            
            if (str(forecaster_type).split('.')[1] == 'ForecasterAutoregMultiVariate') and \
               (series_levels != list(last_window.columns)):
                raise ValueError(
                    (f'`last_window` columns must be the same as `series` column names.\n'
                     f'    `last_window` columns : {list(last_window.columns)}.\n'
                     f'    `series` columns      : {series_levels}.')
                )
        
        else:    
            if not isinstance(last_window, pd.Series):
                raise TypeError('`last_window` must be a pandas Series.')
                
        if last_window.isnull().any().all():
            raise ValueError('`last_window` has missing values.')
        _, last_window_index = preprocess_last_window(
                                    last_window = last_window.iloc[:0]
                                ) 
        if not isinstance(last_window_index, index_type):
            raise TypeError(
                f'Expected index of type {index_type} for `last_window`. '
                f'Got {type(last_window_index)}.'
            )
        if isinstance(last_window_index, pd.DatetimeIndex):
            if not last_window_index.freqstr == index_freq:
                raise TypeError(
                    f'Expected frequency of type {index_freq} for `last_window`. '
                    f'Got {last_window_index.freqstr}.'
                )

    return


def preprocess_y(
    y: pd.Series
) -> Union[np.ndarray, pd.Index]:
    """
    Returns values and index of series separately. Index is overwritten 
    according to the next rules:
        If index is of type DatetimeIndex and has frequency, nothing is 
        changed.
        If index is of type RangeIndex, nothing is changed.
        If index is of type DatetimeIndex but has no frequency, a 
        RangeIndex is created.
        If index is not of type DatetimeIndex, a RangeIndex is created.
    
    Parameters
    ----------        
    y : pandas Series
        Time series.

    Returns 
    -------
    y_values : numpy ndarray
        Numpy array with values of `y`.

    y_index : pandas Index
        Index of `y` modified according to the rules.
    
    """
    
    if isinstance(y.index, pd.DatetimeIndex) and y.index.freq is not None:
        y_index = y.index
    elif isinstance(y.index, pd.RangeIndex):
        y_index = y.index
    elif isinstance(y.index, pd.DatetimeIndex) and y.index.freq is None:
        warnings.warn(
            '`y` has DatetimeIndex index but no frequency. '
            'Index is overwritten with a RangeIndex of step 1.'
        )
        y_index = pd.RangeIndex(
                      start = 0,
                      stop  = len(y),
                      step  = 1
                  )
    else:
        warnings.warn(
            '`y` has no DatetimeIndex nor RangeIndex index. Index is overwritten with a RangeIndex.'
        )
        y_index = pd.RangeIndex(
                      start = 0,
                      stop  = len(y),
                      step  = 1
                  )

    y_values = y.to_numpy()

    return y_values, y_index


def preprocess_last_window(
    last_window:Union[pd.Series, pd.DataFrame]
 ) -> Union[np.ndarray, pd.Index]:
    """
    Returns values and index of series separately. Index is overwritten 
    according to the next rules:
        If index is of type DatetimeIndex and has frequency, nothing is 
        changed.
        If index is of type RangeIndex, nothing is changed.
        If index is of type DatetimeIndex but has no frequency, a 
        RangeIndex is created.
        If index is not of type DatetimeIndex, a RangeIndex is created.
    
    Parameters
    ----------        
    last_window : pandas Series, pandas DataFrame
        Time series values.

    Returns 
    -------
    last_window_values : numpy ndarray
        Numpy array with values of `last_window`.

    last_window_index : pandas Index
        Index of `last_window` modified according to the rules.
    
    """
    
    if isinstance(last_window.index, pd.DatetimeIndex) and last_window.index.freq is not None:
        last_window_index = last_window.index
    elif isinstance(last_window.index, pd.RangeIndex):
        last_window_index = last_window.index
    elif isinstance(last_window.index, pd.DatetimeIndex) and last_window.index.freq is None:
        warnings.warn(
            '`last_window` has DatetimeIndex index but no frequency. '
            'Index is overwritten with a RangeIndex of step 1.'
        )
        last_window_index = pd.RangeIndex(
                                start = 0,
                                stop  = len(last_window),
                                step  = 1
                                )
    else:
        warnings.warn(
            '`last_window` has no DatetimeIndex nor RangeIndex index. Index is overwritten with a RangeIndex.'
        )
        last_window_index = pd.RangeIndex(
                                start = 0,
                                stop  = len(last_window),
                                step  = 1
                                )

    last_window_values = last_window.to_numpy()

    return last_window_values, last_window_index


def preprocess_exog(
    exog: Union[pd.Series, pd.DataFrame]
) -> Union[np.ndarray, pd.Index]:
    """
    Returns values ​​and index of series separately. Index is overwritten 
    according to the next rules:
        If index is of type DatetimeIndex and has frequency, nothing is 
        changed.
        If index is of type RangeIndex, nothing is changed.
        If index is of type DatetimeIndex but has no frequency, a 
        RangeIndex is created.
        If index is not of type DatetimeIndex, a RangeIndex is created.

    Parameters
    ----------        
    exog : pandas Series, pandas DataFrame
        Exogenous variables.

    Returns 
    -------
    exog_values : numpy ndarray
        Numpy array with values of `exog`.

    exog_index : pandas Index
        Index of `exog` modified according to the rules.

    """
    
    if isinstance(exog.index, pd.DatetimeIndex) and exog.index.freq is not None:
        exog_index = exog.index
    elif isinstance(exog.index, pd.RangeIndex):
        exog_index = exog.index
    elif isinstance(exog.index, pd.DatetimeIndex) and exog.index.freq is None:
        warnings.warn(
            '`exog` has DatetimeIndex index but no frequency. '
            'Index is overwritten with a RangeIndex of step 1.'
        )
        exog_index = pd.RangeIndex(
                        start = 0,
                        stop  = len(exog),
                        step  = 1
                        )

    else:
        warnings.warn(
            '`exog` has no DatetimeIndex nor RangeIndex index. Index is overwritten with a RangeIndex.'
        )
        exog_index = pd.RangeIndex(
                        start = 0,
                        stop  = len(exog),
                        step  = 1
                        )

    exog_values = exog.to_numpy()

    return exog_values, exog_index


def exog_to_direct(
    exog: np.ndarray,
    steps: int
)-> np.ndarray:
    """
    Transforms `exog` to `np.ndarray` with the shape needed for direct
    forecasting.
    
    Parameters
    ----------        
    exog : numpy ndarray, shape(samples,)
        Time series values.

    steps : int.
        Number of steps that will be predicted using this exog.

    Returns 
    -------
    exog_transformed : numpy ndarray

    """

    exog_transformed = []

    if exog.ndim < 2:
        exog = exog.reshape(-1, 1)

    for column in range(exog.shape[1]):

        exog_column_transformed = []

        for i in range(exog.shape[0] - (steps -1)):
            exog_column_transformed.append(exog[i:i + steps, column])

        if len(exog_column_transformed) > 1:
            exog_column_transformed = np.vstack(exog_column_transformed)

        exog_transformed.append(exog_column_transformed)

    if len(exog_transformed) > 1:
        exog_transformed = np.hstack(exog_transformed)
    else:
        exog_transformed = exog_column_transformed

    return exog_transformed


def expand_index(
    index: Union[pd.Index, None], 
    steps: int
) -> pd.Index:
    """
    Create a new index of length `steps` starting at the end of the index.
    
    Parameters
    ----------        
    index : pd.Index, None
        Index of last window.
    steps : int
        Number of steps to expand.

    Returns 
    -------
    new_index : pd.Index

    """
    
    if isinstance(index, pd.Index):
        
        if isinstance(index, pd.DatetimeIndex):
            new_index = pd.date_range(
                            index[-1] + index.freq,
                            periods = steps,
                            freq    = index.freq
                        )
        elif isinstance(index, pd.RangeIndex):
            new_index = pd.RangeIndex(
                            start = index[-1] + 1,
                            stop  = index[-1] + 1 + steps
                        )
    else: 
        new_index = pd.RangeIndex(
                        start = 0,
                        stop  = steps
                     )
    return new_index


def transform_series(
    series: pd.Series,
    transformer,
    fit: bool=False,
    inverse_transform: bool=False
) -> Union[pd.Series, pd.DataFrame]:
    """      
    Transform raw values of pandas Series with a scikit-learn alike transformer
    (preprocessor). The transformer used must have the following methods: fit, transform,
    fit_transform and inverse_transform. ColumnTransformers are not allowed since they
    do not have inverse_transform method.

    Parameters
    ----------
    series : pandas Series

    transformer : scikit-learn alike transformer (preprocessor).
        scikit-learn alike transformer (preprocessor) with methods: fit, transform,
        fit_transform and inverse_transform. ColumnTransformers are not allowed since they
        do not have inverse_transform method.

    fit : bool, default `False`
        Train the transformer before applying it.

    inverse_transform : bool, default `False`
        Transform back the data to the original representation.

    Returns
    -------
    series_transformed : pandas Series, pandas DataFrame
        Transformed Series. Depending on the transformer used, the output may be a Series
        or a DataFrame.

    """
    
    if not isinstance(series, pd.Series):
        raise Exception(
            "Series argument must be a pandas Series object."
        )
        
    if transformer is None:
        return series

    series = series.to_frame()

    if fit and not isinstance(transformer, sklearn.preprocessing._function_transformer.FunctionTransformer):
        transformer.fit(series)

    if inverse_transform:
        values_transformed = transformer.inverse_transform(series)
    else:
        values_transformed = transformer.transform(series)   

    if hasattr(values_transformed, 'toarray'):
        # If the returned values are in sparse matrix format, it is converted to dense array.
        values_transformed = values_transformed.toarray()
    
    if isinstance(values_transformed, np.ndarray) and values_transformed.shape[1] == 1:
        series_transformed = pd.Series(
                                 data  = values_transformed.flatten(),
                                 index = series.index,
                                 name  = series.columns[0]
                             )
    elif isinstance(values_transformed, pd.DataFrame) and values_transformed.shape[1] == 1:
        series_transformed = values_transformed.squeeze()
    else:
        series_transformed = pd.DataFrame(
                                 data = values_transformed,
                                 index = series.index,
                                 columns = transformer.get_feature_names_out()
                             )

    return series_transformed


def transform_dataframe(
    df: pd.DataFrame,
    transformer,
    fit: bool=False,
    inverse_transform: bool=False
) -> pd.DataFrame:
    """      
    Transform raw values of pandas DataFrame with a scikit-learn alike
    transformer, preprocessor or ColumnTransformer. `inverse_transform` is not available
    when using ColumnTransformers.

    Parameters
    ----------
    series : pandas DataFrame

    transformer : scikit-learn alike transformer, preprocessor or ColumnTransformer.
        scikit-learn alike transformer, preprocessor or ColumnTransformer.

    fit : bool, default `False`
        Train the transformer before applying it.

    inverse_transform : bool, default `False`
        Transform back the data to the original representation. This is not available
        when using transformers of class scikit-learn ColumnTransformers.

    Returns
    -------
    series_transformed : pandas DataFrame
        Transformed DataFrame.
    
    """

    if transformer is None:
        return df

    if inverse_transform and\
    isinstance(transformer, sklearn.compose._column_transformer.ColumnTransformer):
        raise Exception(
            '`inverse_transform` is not available when using ColumnTransformers.'
        )
    
    if not inverse_transform:
        if fit:
            values_transformed = transformer.fit_transform(df)
        else:
            values_transformed = transformer.transform(df)
    else:
        values_transformed = transformer.inverse_transform(df)

    if hasattr(values_transformed, 'toarray'):
        # If the returned values are in sparse matrix format, it is converted to dense
        values_transformed = values_transformed.toarray()

    if hasattr(transformer, 'get_feature_names_out'):
        feature_names_out = transformer.get_feature_names_out()
    elif hasattr(transformer, 'categories_'):   
        feature_names_out = transformer.categories_
    else:
        feature_names_out = df.columns
    
    df_transformed = pd.DataFrame(
                         data = values_transformed,
                         index = df.index,
                         columns = feature_names_out
                     )

    return df_transformed


def save_forecaster(
    forecaster, 
    file_name: str, 
    verbose: bool=True
) -> None:
    """
    Save forecaster model using joblib.

    Parameters
    ----------
    forecaster: forecaster object from skforecast library.
        Model created with skforecast library.

    file_name: str
        File name given to the object.
        
    verbose: bool, default `True`
        Print info about the forecaster saved

    Returns 
    -------
    None

    """

    joblib.dump(forecaster, filename=file_name)

    if verbose:
        forecaster.summary()


def load_forecaster(
    file_name: str,
    verbose: bool=True
):
    """
    Load forecaster model from disc using joblib.

    Parameters
    ----------
    forecaster: forecaster object from skforecast library.
        Forecaster created with skforecast library.

    file_name: str
        File name given to the object.

    verbose: bool, default `True`
        Print summary about the forecaster loaded.

    Returns 
    -------
    Forecaster
        Forecaster created with skforecast library.
    
    """

    forecaster = joblib.load(filename=file_name)

    if verbose:
        forecaster.summary()

    return forecaster