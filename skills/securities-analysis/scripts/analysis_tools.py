#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
证券分析工具集
提供技术分析指标计算、数据处理等核心功能
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional


class TechnicalIndicators:
    """技术指标计算类"""
    
    @staticmethod
    def moving_average(data: pd.Series, window: int) -> pd.Series:
        """
        计算移动平均线
        
        参数:
            data: 价格序列
            window: 窗口大小
            
        返回:
            移动平均线序列
        """
        return data.rolling(window=window).mean()
    
    @staticmethod
    def exponential_moving_average(data: pd.Series, window: int) -> pd.Series:
        """
        计算指数移动平均线
        
        参数:
            data: 价格序列
            window: 窗口大小
            
        返回:
            指数移动平均线序列
        """
        return data.ewm(span=window, adjust=False).mean()
    
    @staticmethod
    def macd(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """
        计算MACD指标
        
        参数:
            data: 价格序列
            fast: 快线周期
            slow: 慢线周期
            signal: 信号线周期
            
        返回:
            包含MACD、信号线、柱线的字典
        """
        ema_fast = TechnicalIndicators.exponential_moving_average(data, fast)
        ema_slow = TechnicalIndicators.exponential_moving_average(data, slow)
        
        macd_line = ema_fast - ema_slow
        signal_line = TechnicalIndicators.exponential_moving_average(macd_line, signal)
        histogram = macd_line - signal_line
        
        return {
            'MACD': macd_line,
            'Signal': signal_line,
            'Histogram': histogram
        }
    
    @staticmethod
    def rsi(data: pd.Series, window: int = 14) -> pd.Series:
        """
        计算RSI相对强弱指标
        
        参数:
            data: 价格序列
            window: 窗口大小
            
        返回:
            RSI序列
        """
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def bollinger_bands(data: pd.Series, window: int = 20, num_std: float = 2.0) -> Dict[str, pd.Series]:
        """
        计算布林带
        
        参数:
            data: 价格序列
            window: 窗口大小
            num_std: 标准差倍数
            
        返回:
            包含上轨、中轨、下轨的字典
        """
        sma = TechnicalIndicators.moving_average(data, window)
        std = data.rolling(window=window).std()
        
        upper_band = sma + (std * num_std)
        lower_band = sma - (std * num_std)
        
        return {
            'Upper': upper_band,
            'Middle': sma,
            'Lower': lower_band
        }
    
    @staticmethod
    def kdj(data: pd.DataFrame, n: int = 9, m1: int = 3, m2: int = 3) -> Dict[str, pd.Series]:
        """
        计算KDJ指标
        
        参数:
            data: 包含High、Low、Close的DataFrame
            n: 周期
            m1: K线平滑周期
            m2: J线平滑周期
            
        返回:
            包含K、D、J的字典
        """
        high = data['High']
        low = data['Low']
        close = data['Close']
        
        llv_low = low.rolling(window=n).min()
        hlv_high = high.rolling(window=n).max()
        
        rsv = (close - llv_low) / (hlv_high - llv_low) * 100
        
        k = rsv.ewm(com=m1-1, adjust=False).mean()
        d = k.ewm(com=m2-1, adjust=False).mean()
        j = 3 * k - 2 * d
        
        return {
            'K': k,
            'D': d,
            'J': j
        }


class FundamentalAnalysis:
    """基本面分析类"""
    
    @staticmethod
    def calculate_roe(net_income: float, equity: float) -> float:
        """
        计算净资产收益率(ROE)
        
        参数:
            net_income: 净利润
            equity: 净资产
            
        返回:
            ROE值（百分比）
        """
        if equity == 0:
            return 0.0
        return (net_income / equity) * 100
    
    @staticmethod
    def calculate_roa(net_income: float, total_assets: float) -> float:
        """
        计算总资产收益率(ROA)
        
        参数:
            net_income: 净利润
            total_assets: 总资产
            
        返回:
            ROA值（百分比）
        """
        if total_assets == 0:
            return 0.0
        return (net_income / total_assets) * 100
    
    @staticmethod
    def calculate_pe_ratio(price: float, eps: float) -> float:
        """
        计算市盈率(PE)
        
        参数:
            price: 股价
            eps: 每股收益
            
        返回:
            PE值
        """
        if eps == 0:
            return 0.0
        return price / eps
    
    @staticmethod
    def calculate_pb_ratio(price: float, book_value_per_share: float) -> float:
        """
        计算市净率(PB)
        
        参数:
            price: 股价
            book_value_per_share: 每股净资产
            
        返回:
            PB值
        """
        if book_value_per_share == 0:
            return 0.0
        return price / book_value_per_share
    
    @staticmethod
    def calculate_debt_ratio(total_liabilities: float, total_assets: float) -> float:
        """
        计算资产负债率
        
        参数:
            total_liabilities: 总负债
            total_assets: 总资产
            
        返回:
            资产负债率（百分比）
        """
        if total_assets == 0:
            return 0.0
        return (total_liabilities / total_assets) * 100
    
    @staticmethod
    def calculate_current_ratio(current_assets: float, current_liabilities: float) -> float:
        """
        计算流动比率
        
        参数:
            current_assets: 流动资产
            current_liabilities: 流动负债
            
        返回:
            流动比率
        """
        if current_liabilities == 0:
            return 0.0
        return current_assets / current_liabilities


def support_resistance_levels(prices: pd.Series, window: int = 20, 
                              num_levels: int = 3) -> Tuple[List[float], List[float]]:
    """
    识别支撑位和阻力位
    
    参数:
        prices: 价格序列
        window: 窗口大小
        num_levels: 识别的价位数量
        
    返回:
        (支撑位列表, 阻力位列表)
    """
    # 找到局部低点作为支撑位
    lows = prices.rolling(window=window, center=True).min()
    support_candidates = prices[prices == lows].unique()
    
    # 找到局部高点作为阻力位
    highs = prices.rolling(window=window, center=True).max()
    resistance_candidates = prices[prices == highs].unique()
    
    # 过滤并排序
    support_levels = sorted(support_candidates[support_candidates > 0], reverse=True)[:num_levels]
    resistance_levels = sorted(resistance_candidates[resistance_candidates > 0])[:num_levels]
    
    return support_levels, resistance_levels


if __name__ == "__main__":
    # 测试代码
    print("证券分析工具集已加载")
