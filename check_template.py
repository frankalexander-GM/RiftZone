import re
content = open('app/templates/jugador/clanes.html', 'r', encoding='utf-8').read()
# Count divs
opens = content.count('<div')
closes = content.count('</div>')
print(f'clanes.html: <div>={opens}, </div>={closes}, diff={opens-closes}')

opens2 = content.count('<span')
closes2 = content.count('</span>')
print(f'clanes.html: <span>={opens2}, </span>={closes2}, diff={opens2-closes2}')
