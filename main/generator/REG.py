import operator

def proper_name(rule):
    graph = rule.graph
    names = []
    for node in graph.nodes:
        parent = graph.nodes[node].parent
        if ':op' in parent['edge']:
            names.append((parent['edge'], node))
    names.sort(key=operator.itemgetter(0))

    name = ' '.join(map(lambda x: x[1], names))
    return name.strip()

def have_role(rule):
    graph = rule.graph
    name = ''
    for node in graph.nodes:
        parent = graph.nodes[node].parent
        if parent['edge'] == ':arg2':
            name = node
            break
    return name

def date_entity(rule):
    graph = rule.graph
    day, month, year = '', '', ''
    for node in graph.nodes:
        parent = graph.nodes[node].parent
        if 'year' in parent['edge']:
            year = node
        elif 'month' in parent['edge']:
            month = node
        elif 'day' in parent['edge']:
            day = node

    if month == '1': month = 'January'
    elif month == '2': month = 'February'
    elif month == '3': month = 'March'
    elif month == '4': month = 'April'
    elif month == '5': month = 'May'
    elif month == '6': month = 'June'
    elif month == '7': month = 'July'
    elif month == '8': month = 'August'
    elif month == '9': month = 'September'
    elif month == '10': month = 'October'
    elif month == '11': month = 'November'
    elif month == '12': month = 'December'

    date = ''
    if month != '':
        date = month
        if day != '':
            if day == '1':
                date = date + ' ' + day + 'st'
            elif day == '1':
                date = date + ' ' + day + 'nd'
            elif day == '1':
                date = date + ' ' + day + 'rd'
            else:
                date = date + ' ' + day + 'th'
        if year != '':
            date = date + ', ' + year
    elif year != '':
        date = year

    return date
