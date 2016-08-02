import random
import string
import os

from django.db import models
from django.utils.timezone import now as timezone_now


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text


class Posto(models.Model):
    nome = models.CharField(max_length=100)
    nome_fantasia = models.CharField(max_length=100)
    endereco = models.CharField(max_length=200)
    bairro = models.CharField(max_length=50)
    cnpj = models.CharField(max_length=20)

    def __str__(self):
        return self.nome


class Laudo(models.Model):
    posto = models.ForeignKey('Posto', on_delete=models.CASCADE, default=None)

    numero_proposta = models.CharField(max_length=15)

    registro_anp_definitivo = models.NullBooleanField()
    registro_anp_numero = models.CharField(max_length=50, null=True)
    registro_anp_data_expedicao = models.DateField(null=True)
    registro_anp_data_validade = models.DateField(null=True)
    alvara_funcionamento_definitivo = models.NullBooleanField()
    alvara_funcionamento_numero = models.CharField(max_length=50, null=True)
    alvara_funcionamento_data_expedicao = models.DateField(null=True)
    alvara_funcionamento_data_validade = models.DateField(null=True)

    # 0 - LP, 1 - LI, 2 - LO
    licenca_ambiental = models.IntegerField(null=True)
    licenca_ambiental_numero = models.CharField(max_length=50, null=True)
    licenca_ambiental_data_expedicao = models.DateField(null=True)
    licenca_ambiental_data_validade = models.DateField(null=True)
    atestado_regularidade_ar_sim = models.BooleanField()
    atestado_regularidade_ar_numero = models.CharField(max_length=50, null=True)
    atestado_regularidade_ar_data_expedicao = models.DateField(null=True)
    atestado_regularidade_ar_data_validade = models.DateField(null=True)
    observacao = models.CharField(max_length=300, null=True)

    venda_combustiveis_disponivel = models.BooleanField()
    lavagem_viculos_disponivel = models.BooleanField()
    restaurante_lanchonete_conveniencia_disponivel = models.BooleanField()
    troca_oleo_disponivel = models.BooleanField()
    oficina_mecanica_disponivel = models.BooleanField()
    venda_gas_cozinha = models.BooleanField()
    outros_servicos_disponibilidade = models.CharField(max_length=300)

    # Integer fields: 0 - Precario, 1 - Regular, 2 - Bom
    valvula_retentora_vapor_disponibilidade = models.BooleanField()
    valvula_retentora_vapor_estado_conservacao = models.IntegerField(null=True)
    tanque_sub_parede_dupla_jaquetado = models.BooleanField()
    tanque_sub_parede_data_instalacao = models.DateField(null=True)
    poco_monitoramento_disponibilidade = models.BooleanField()
    poco_monitoramento_estado_conservacao = models.IntegerField(null=True)
    caneletas_ilhas_bombas_disponibilidade = models.BooleanField()
    caneletas_ilhas_bombas_estado_conservacao = models.IntegerField(null=True)
    caneletas_perimetro_disponibilidade = models.BooleanField()
    caneletas_perimetro_estado_conservacao = models.IntegerField(null=True)
    piso_concreto_alisado_disponibilidade = models.BooleanField()
    piso_concreto_alisado_estado_conservacao = models.IntegerField(null=True)
    caneletas_interligadas_sao_disponibilidade = models.BooleanField()
    caneletas_interligadas_sao_estado_conservacao = models.IntegerField(null=True)
    sistema_deteccao_vazamento_disponibilidade = models.BooleanField()
    sistema_deteccao_vazamento_estado_conservacao = models.IntegerField(null=True)

    area_lavagem_piso_can_sao_disponibilidade = models.BooleanField()
    area_lavagem_piso_can_sao_estado_conservacao = models.IntegerField(null=True)
    area_troca_oleo_piso_can_sao_disponibilidade = models.BooleanField()
    area_troca_oleo_piso_can_sao_estado_conservacao = models.IntegerField(null=True)
    area_armazenamento_residuos_coberta_piso_disponibilidade = models.BooleanField()
    area_armazenamento_residuos_coberta_piso_estado_conservacao = models.IntegerField(null=True)
    atendido_rede_publica_saneamento = models.BooleanField()
    quantidade_tanques = models.IntegerField(null=True)
    capacidade_armazenamento = models.IntegerField(default=0)

    houve_sinistro_ultimos_anos = models.BooleanField()
    prejuizo_estimativa = models.DecimalField(decimal_places=2, max_digits=20, null=True)
    data_sinistro = models.DateField(null=True)
    ocorrencia = models.CharField(max_length=300, null=True)

    def __str__(self):
        return self.posto.nome + ' - ' + self.numero_proposta
