import pytholog as pl
kb = pl.KnowledgeBase("KB")

knowledge = ['male(ali)',
             'male(ahmed)',
             'female(ayesha)',
             'parent(ali, ahmed)',
             'parent(ahmed, ayesha)',
             'father(X, Y):-male(X), parent(X, Y)']

with open(r'pytholog_kb.pl', 'w') as file:
    for item in knowledge:
        file.write(item + '\n')
    

new_fact = input('Enter new fact: ')
if new_fact:
    with open(r'pytholog_kb.pl', 'a') as file:
        file.write('\n' + new_fact)
else:
    print('No new fact added!')


with open(r'pytholog_kb.pl', 'r') as file:
    
    knowledge = file.readlines()


knowledge = [item.strip() for item in knowledge]
kb(knowledge)

query = input('Enter Prolog query: ')
result = kb.query(pl.Expr(query))
print(type(result))
for i in result:
    print(i)
