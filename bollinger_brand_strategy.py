def bollinger_brand_strategy(train_data,df_arr,time_arr):


    fund = 1000000
    stockfee_precent =  0.001425 # 證卷手續費
    exchangefee_precent = 0.003  # 交易所手續費
    length = 20
    NumStd = 1.5
    K = 0.15
    NumStock = 1000 # 每次交易一張（1000股）

    BS = None
    buy = []
    sell = []
    sellshort = []
    buytocover = []
    profit_list = [0]
    profit_fee_list = [0]
    profit_fee_list_realized = []
    rets = []

    for i in range(len(df_arr)):

        if i == len(df_arr)-1:
            break

        ## 進場邏輯
        # 當收盤價突破布林上軌，做多入場
        entryLong = df_arr[i,4] > df_arr[i,9]
        # 當收盤價跌破布林下軌，做空入場
        entrySellShort = df_arr[i,4] < df_arr[i,10]

        ## 出場邏輯
        # 當收盤價跌破布林上軌，做多出場
        exitShort = df_arr[i,4] <= df_arr[i,9]
        # 當收盤價突破布林下軌，做空出場
        exitBuyToCover = df_arr[i,4] >= df_arr[i,10]

        ## 停利停損邏輯
        # 做多
        if BS == 'B':
            stopLoss = df_arr[i,4] <= df_arr[t,1] * (1-K)
            stopProfit = df_arr[i,4] >= df_arr[t,1] * (1+K)
        # 做空
        elif BS == 'S':
            stopLoss = df_arr[i,4] >= df_arr[t,1] * (1+K)
            stopProfit = df_arr[i,4] <= df_arr[t,1] * (1-K)

        ##還沒進場不用計算損益
        if BS == None:
            profit_list.append(0)
            profit_fee_list.append(0)

            if entryLong :
                BS = 'B'
                t = i+1
                buy.append(t)
                print("Enter Long Position")
                print("Buy Price: {}, time: {}".format(df_arr[t,1], time_arr[t]))

            elif entrySellShort:
                BS = 'S'
                t = i+1
                sellshort.append(t)
                print("Enter Short Position")
                print("Sell Price: {}, time: {}".format(df_arr[t,1], time_arr[t]))

        #進場開始計算未實現損益
        elif BS == 'B':
            profit = (df_arr[i+1,1] - df_arr[i,1])*NumStock
            profit_list.append(profit)
            
            #近場條件達成，計算未實現損益-交易成本
            if exitShort  or stopLoss or stopProfit:
                pl_round = (df_arr[i+1,1] - df_arr[i,1])*NumStock
                profit_fee = profit - df_arr[i+1,1]*NumStock*(stockfee_precent+exchangefee_precent)
                profit_fee_list.append(profit_fee)
                sell.append(i+1)
                BS=None
                print("Sell Price: {}, time: {}".format(df_arr[i+1,1], time_arr[i+1]))
                print("Trade completed")
                print()

                # 以實現盈虧
                profit_fee_realized = pl_round - profit_fee
                profit_fee_list_realized.append(profit_fee_realized)
                rets.append(profit_fee_realized/(df_arr[t,1]))

            else:
                profit_fee = profit
                profit_fee_list.append(profit_fee)

        elif BS == 'S':
            profit = (df_arr[i,1] - df_arr[i+1,1])*NumStock
            profit_list.append(profit)

            #出場條件達成，計算未實現損益-交易成本
            if exitBuyToCover   or stopLoss or stopProfit:
                pl_round = (df_arr[t,1] - df_arr[i+1,1])*NumStock
                profit_fee =  profit - df_arr[i+1,1]*NumStock*stockfee_precent
                profit_fee_list.append(profit_fee)
                buytocover.append(i+1)
                BS = None
                print("Buycover Price: {}, time: {}".format(df_arr[i+1,1], time_arr[i+1]))
                print("Trade completed")
                print()

                # Realized PnL
                profit_fee_realized = pl_round - profit_fee
                profit_fee_list_realized.append(profit_fee_realized)
                rets.append(profit_fee_realized/(NumStock*df_arr[t,1]))

            else:
                profit_fee = profit
                profit_fee_list.append(profit_fee)


        equity = pd.DataFrame({'profit':np.cumsum(profit_list), 'profitfee':np.cumsum(profit_fee_list)}, index=train_data['Date'])
        return equity
