from ucollections import OrderedDict



def cdf_cal(time_list):
    """ Calculates the cdf for the time delay
    :param list: the list of times
    """
    results_sum = OrderedDict()
    for time in time_list:
        print("time:{}".format(time))
        round_time = round(time,3)
        print("round_time:{}".format(round_time))
        if round_time in results_sum:
            results_sum[round_time] +=1
        else:
            results_sum[round_time] = 1
        #print("results_sum -> {}".format(results_sum))

    for time_delay in results_sum:
        results_sum[time_delay] = results_sum[time_delay] / len(time_list)
    
    #print("results_sum -> {}".format(results_sum))
