# -*- coding: utf-8 -*-

"""
Fuctions relating to the calculation of multi asset indices 

"""


import pnadas as pd 
import numpy as np 


def sq_log_ret(series : pd.Series) -> pd.Series:
    """
    Takes a series and converts it to another series wehre we 
    take the squared differences of the logs of the initial series. 
    
    differenced logs are akin to % change - squaring rids of negatives & amplifies 
    small differences. 

    Parameters
    ----------
    series : pd.Series
        any seires of int/floats.

    Returns
    -------
    sq_log_ret : pd.Series
        initial series converted. 

    """
    
    return np.log(series.diff()) ** 2



def nci_vwaps_volatility_volumes(trades:pd.DataFrame, rvs: pd.DataFrame) -> pd.DataFrame:
    """
    Function builds the basis of the 'log/coin' files which contain the 
    aggregated/underlying prices for the nci indices 

    Parameters
    ----------
    trades : pd.DataFrame
        DESCRIPTION.
    rvs : pd.DataFrame
        DESCRIPTION.

    Returns
    -------
    None.

    """
    
    trades['TM'] = trades['TS'].apply(lambda x:x -x%60)
    
    trades.sort_values("TM", inplace=True)
    
    vwaps = (trades[["FSYM","M", "Q","TOTAL","TM"]]).groupby(["FSYM","M","TM"]).sum().reset_index()
    
    vwaps['vwap'] = vwaps['TOTAL'] / vwaps['Q']
    
    vwaps['sq_log_ret'] = vwaps['vwap'].groupby(['FSYM','M']).apply(sq_log_ret).reset_index()
    
    df = (
        vwaps[['vwap','Q','sq_log_ret']].groupby(['FSYM','M']).agg(price=("vwap","mean"),
                                                                   volume=("Q","sum"),
                                                                   volatility=("sq_log_ret","sum")))
    
    rvs['exchange'] = rvs['exchange'].str.capitalize()
    
    rvs['exchange'] = rvs['exchange'].replace({'Itbit':'itBit'})
    
    rvs.rename(columns={'exchange':'M','fromsymbol':'FSYM'},inplace=True)
    
    df['rv'] = ( rvs[['quantity','M','FSYM']].groupby(['FSYM','M']).agg(rv=("quantity",'median')))
    
    df['normal_volume'] = df['volume'] / df['rv']
    
    df.dropna(inplace=True)
    
    return df



def nci_penalties(components:list, inputs: pd.DataFrame) -> dict:
    """
    fucntion builds the coin/log files for each asset which constitues the index
    decides the constituent exchange weights by calculating penalites. 
    
    Penalties only calced when more than 2 exchanges have price data for a given exchange, else all penalties 
    are set to 1. 
    
    as std is caled for the price (twaps), volatility (sum of squared logs) and normal volume (todays Q / median 30 day vol)
    there must be vairation across all, have been edge cases where 3 or more exchange have the same twap price (unlikley)

    Parameters
    ----------
    components : list
        list of assets in index.
    inputs : pd.DataFrame
        base of coin/log files - containing twaps, volatility, rv, q & normal voumes.

    Returns
    -------
    dict
        with assets as keys & coin/log files as values.

    """
    
    dict_coins = {}
    
    for asset in components:
        
        df_coin = inputs[inputs['FSYM'] == asset].copy()
        
        if len(df_coin) > 2:
            
            if df_coin['price'].std() !=0:
                
                df_coin['c_price'] = df_coin['price'].apply(
                    lambda x: 1 / max(1,abs(x - df_coin['price'].median())/df_coin['price'].std()))
                
            else:
                
                df_coin['c_price'] = 1
                
            if df_coin['normal_volume'].std() !=0:
                
                df_coin['c_volume'] = df_coin['normal_volume'].apply(
                    lambda x: 1 / max(1,abs(x - df_coin['normal_volume'].median())/df_coin['normal_volume'].std()))
                
            else:
                
                df_coin['c_volume'] = 1 

                
            if df_coin['volatility'].std() !=0:
                
                df_coin['c_volatility'] = df_coin['volatility'].apply(
                    lambda x: 1 / max(1,abs(x - df_coin['volatility'].median())/df_coin['volatility'].std()))
                
            else: 
                
                df_coin['c_volatility'] = 1
                
        else:
            
            df_coin['c_price'] = 1 
            df_coin['c_volume'] = 1 
            df_coin['c_volatility'] = 1 
            
            
        df_coin['weights_aux'] = (
            df_coin['rv']
            * df_coin['c_price']
            * df_coin['c_volatility']
            * df_coin['c_volatility']
            )
        
        df_coin['weights'] = df_coin['weights_aux'].apply(lambda x : x /df_coin['weights_aux'].sum())
        
        dict_coins[asset]= df_coin
        
        
    return dict_coins


def nci_mc_calc(assets: list, coin_logs : dict, config:pd.DataFrame, divisor:float, prev_prices:pd.DataFrame) -> [float, pd.DataFrame]:
    """
    Fucntion generates the final aggregated (underlying price) for each asset, calcs the daily index weights (share each asset has in total index market share)
    and calcs index value which is the Total MC of index / divisor (to keep index in reference to initial value).
    
    if no trade data available use last prev day price. 

    Parameters
    ----------
    coin_logs : dict
        DESCRIPTION.
    config : pd.DataFrame
        DESCRIPTION.
    divisor : float
        DESCRIPTION.
    prev_prices : pd.DataFrame
        DESCRIPTION.

    Returns
    -------
    None.

    """
    underlyings = {}
        
    for asset in assets:
        
        if asset in coin_logs:
        
            underlyings[asset] = (( coin_logs[asset]['price'] * coin_logs[asset]['weights']).sum()).round(4)
          
        else:
             
            underlyings[asset] = prev_prices[prev_prices['Constituent Symbol'] == asset]['Price USD'].iloc[0]
            
    df_u = pd.DataFrame.from_dict(underlyings, orient="index", columns=['ncis'])
    
    df_u['Index Weight'] = config['Amount'] * df_u['ncis'].apply(lambda x : x / config['Amount'] * df_u['ncis'].sum())
    
    # index weight is the daily close share in the market cap each asset has in the total MC of the index. 
    
    index_value = df_u['ncis'] * config['Amount'].sum() / divisor
    
    # final index value is the sum of the index market cap (P*supply) over divisor - initial value scaled by base day MC (adjusted for increases in Q)
    
    return index_value, df_u





def mv_mc_calc()




        
        
             
            
        
        
        
        
        
        
        
        

                              
                
                 
    
    
    
    
    
    
    
    