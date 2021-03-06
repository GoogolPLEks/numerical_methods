from multiprocessing import Pool, cpu_count
import time
import random

import numpy as np

from data import flights, peoples

"""
Планирование путешествия группы людей, которые, отправляясь из разных мест, 
должны прибыть в одно и то же место.

Люди эти живут в разных концах страны и хотят встретиться в определенном месте.
Все они должны вылететь в один день и в один день улететь и при этом в 
целях экономии хотели бы уехать из аэропорта
и приехать в него на одной арендованной машине.
Ежедневно, в город места назначения, из мест проживания этих людей отправляются десятки рейсов,
все в разное время.

Цена билета и время в пути для каждого рейса разные.

Даны расписания рейсов из каждого искомого города до общего места назначения.
Необходимо расчитать минимальную общую цену с помощью алгоритма случайного поиска

Программа уже написана(я же обещал упростить условия))). Нужно распараллелить алгоритм с 
помощью питоновских библиотек(гугл в помощь) и сравнить с однопоточной версией
"""


def random_optimize(domain, costf, is_parallel=True):
    """
    Function of random search
    :param domain: list of pair: (air to, air from) and (air from, air to)
    :param costf: it is function who calculate cost
    :param is_parallel: if True then parallel
    :return: final cost of travel
    """

    if is_parallel:
        pool = Pool(processes=cpu_count())
        solutions = pool.map(costf, [[random.randint(0, dmn) for dmn in domain] for i in range(1000)])
        solution = min(solutions, key=lambda sol: sol[1])
    else:
        solutions = map(costf, [[random.randint(0, dmn) for dmn in domain] for i in range(1000)])
        solution = min(solutions, key=lambda sol: sol[1])

    return solution


def get_minutes(t):
    x = time.strptime(t, '%H:%M')
    return x[3] * 60 + x[4]


def get_flights_info(d, sol):
    """
    :param d: number person in list peoples
    :param sol: random solution
    :return: tuple (outbound time, return time, total cost flight)
    """
    origin = peoples[d][1]
    outbound = flights[(origin, destination)][sol[2 * d]]
    returnf = flights[(destination, origin)][int(sol[2 * d + 1])]
    return [returnf[0], outbound[1], outbound[2] + returnf[2]]


def schedule_cost(sol):

    info_flights = [get_flights_info(d, sol) for d in range(len(peoples))]
    totalprice = sum([flight[2] for flight in info_flights])
    latestarrival = get_minutes(max(info_flights, key=lambda flight: get_minutes(flight[1]))[1])
    earliestdep = get_minutes(min(info_flights, key=lambda flight: get_minutes(flight[0]))[0])

    totalwait = sum([latestarrival - get_minutes(f[1]) + get_minutes(f[0]) - earliestdep
                     for f in info_flights])

    if latestarrival > earliestdep:
        totalprice += 50

    return sol, totalprice + totalwait


if __name__ == '__main__':

    # место назначения
    destination = 'LGA'

    domain = []
    for people in peoples:
        domain.append(len(flights[(people[1], destination)]) - 1)
        domain.append(len(flights[(destination, people[1])]) - 1)

    time_results_with_parallel = []
    time_results_without_parallel = []
    for _ in range(100):
        start_time = time.time()
        random_optimize(domain, schedule_cost)
        time_results_with_parallel.append(time.time() - start_time)

    for _ in range(100):
        start_time = time.time()
        random_optimize(domain, schedule_cost, False)
        time_results_without_parallel.append(time.time() - start_time)

    print("--- Time work with parallel = %s seconds ---" % np.mean(time_results_with_parallel))
    print("--- Time work without parallel = %s seconds ---" % np.mean(time_results_without_parallel))

