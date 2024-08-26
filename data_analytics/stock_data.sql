
'''Average Daily Closing Price Over a Period'''

SELECT 
    AVG(Close) AS Average_Closing_Price
FROM 
    stock_data
WHERE 
    Date BETWEEN '2023-08-24' AND '2023-08-29';

'''Highest and Lowest Prices During a Period'''
SELECT 
    MAX(High) AS Highest_Price,
    MIN(Low) AS Lowest_Price
FROM 
    stock_data
WHERE 
    Date BETWEEN '2023-08-24' AND '2023-08-29';

'''Daily Trading Volume'''
SELECT 
    Date,
    SUM(Volume) AS Total_Volume
FROM 
    stock_data
GROUP BY 
    Date
ORDER BY 
    Date;

'''Price Change Analysis'''
SELECT 
    Date,
    (Close - Open) AS Price_Change
FROM 
    stock_data
ORDER BY 
    Date;


'''Identify Days with Significant Price Changes'''
SELECT 
    Date,
    Close,
    Open,
    (Close - Open) AS Price_Change
FROM 
    stock_data
WHERE 
    ABS(Close - Open) > 2  -- Threshold for significant change
ORDER BY 
    Date;
