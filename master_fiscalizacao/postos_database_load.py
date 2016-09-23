from formulario_vistoria.models import Posto
import django

    
f = open("PLANILHA POSTOS - BASE DE CADASTRO.csv", 'r')
lines = f.readlines()

Posto.objects.all().delete()

for i, line in enumerate(lines[1:]):
    print(float(i) / len(lines[1:]))
    line = line.split('\n')[0]
    data = (line.split(';'))
    posto = Posto(nome=data[1], endereco=data[2], bairro=data[3], cnpj=data[4])
    posto.save()
