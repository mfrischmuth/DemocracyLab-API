import math


def Corr(x, y):
    n = len(x)
    sumX = sumY = sum_X_Square = sum_Y_Square = sum_XY = 0
    for i in range(n):
        sumX = sumX + x[i]
        sum_X_Square = sum_X_Square + x[i]*x[i]
        sumY = sumY + y[i]
        sum_Y_Square = sum_Y_Square + y[i]*y[i]
        sum_XY = sum_XY + x[i]*y[i]

    D1 = n*sum_X_Square - sumX*sumX
    D2 = n*sum_Y_Square - sumY*sumY
    if D1 == 0 or D2 == 0:
        return 1
    return (n*sum_XY - sumX*sumY)/math.sqrt(
        (n*sum_X_Square - sumX*sumX)*(n*sum_Y_Square-sumY*sumY))


# print Corr([-2,-5,-6],[1,4,3])
