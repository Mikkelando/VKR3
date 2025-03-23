from bisect import bisect

def process_ch4nat_entry(entry):
    year, value = entry.strip().split()
    return int(year), float(value)

def process_forcother_entry(entry):
    year, co2f, ch4f, totalf = entry.strip().split()
    return int(year), float(totalf) - float(co2f) - float(ch4f)

CH4NAT = []
FORCOTHER = []
LOADED = False

def load():
    global LOADED
    if LOADED:
        return
    for dataset in ['ch4nat', 'forcother']:
        process = globals()['process_' + dataset + '_entry']
        for scenario in range(1, 6):
            globals()[dataset.upper()].append([
                process(line) for line in open(f'ssp/{dataset}_{scenario}.txt')
            ])
    LOADED = True

def ssp_value(dataset, scenario, year):
    load()
    data = globals()[dataset.upper()][scenario - 1]
    index = bisect(data, (year, 0.))
    if index == 0:
        return data[0][1]
    if index == len(data):
        return data[-1][1]
    l_year, l_value = data[index - 1]
    r_year, r_value = data[index]
    return (l_value * (r_year - year) + r_value * (year - l_year)) / (r_year - l_year)

def ssp_ch4nat(scenario, year):
    return ssp_value('ch4nat', scenario, year)

def ssp_forcother(scenario, year):
    return ssp_value('forcother', scenario, year)
