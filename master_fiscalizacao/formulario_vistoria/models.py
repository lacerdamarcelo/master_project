from django.db import models
from django.contrib.auth.models import User


class Posto(models.Model):
    nome = models.CharField(max_length=100)
    nome_fantasia = models.CharField(max_length=100)
    endereco = models.CharField(max_length=200)
    bairro = models.CharField(max_length=50)
    cnpj = models.CharField(max_length=20)

    def __str__(self):
        return self.nome


class Laudo(models.Model):
    data_criacao = models.DateField()
    data_permissao = models.DateField(null=True)

    status = models.IntegerField()

    posto = models.ForeignKey('Posto', on_delete=models.CASCADE, default=None)

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, default=None, null=True)

    numero_proposta = models.CharField(max_length=15)

    registro_anp_definitivo = models.NullBooleanField(null=True)
    registro_anp_numero = models.CharField(max_length=50, null=True)
    registro_anp_data_expedicao = models.DateField(null=True)
    registro_anp_data_validade = models.DateField(null=True)
    alvara_funcionamento_definitivo = models.NullBooleanField(null=True)
    alvara_funcionamento_numero = models.CharField(max_length=50, null=True)
    alvara_funcionamento_data_expedicao = models.DateField(null=True)
    alvara_funcionamento_data_validade = models.DateField(null=True)

    # 0 - LP, 1 - LI, 2 - LO
    licenca_ambiental = models.IntegerField(null=True)
    licenca_ambiental_numero = models.CharField(max_length=50, null=True)
    licenca_ambiental_data_expedicao = models.DateField(null=True)
    licenca_ambiental_data_validade = models.DateField(null=True)
    atestado_regularidade_ar_sim = models.NullBooleanField(null=True)
    atestado_regularidade_ar_numero = models.CharField(max_length=50, null=True)
    atestado_regularidade_ar_data_expedicao = models.DateField(null=True)
    atestado_regularidade_ar_data_validade = models.DateField(null=True)
    observacao = models.CharField(max_length=300, null=True)

    venda_combustiveis_disponivel = models.NullBooleanField(null=True)
    lavagem_viculos_disponivel = models.NullBooleanField(null=True)
    restaurante_lanchonete_conveniencia_disponivel = models.NullBooleanField(null=True)
    troca_oleo_disponivel = models.NullBooleanField(null=True)
    oficina_mecanica_disponivel = models.NullBooleanField(null=True)
    venda_gas_cozinha = models.NullBooleanField(null=True)
    outros_servicos_disponibilidade = models.CharField(max_length=300, null=True)

    # Integer fields: 0 - Precario, 1 - Regular, 2 - Bom
    valvula_retentora_vapor_disponibilidade = models.NullBooleanField(null=True)
    valvula_retentora_vapor_estado_conservacao = models.IntegerField(null=True)
    tanque_sub_parede_dupla_jaquetado = models.NullBooleanField(null=True)
    tanque_sub_parede_data_instalacao = models.DateField(null=True)
    poco_monitoramento_disponibilidade = models.NullBooleanField(null=True)
    poco_monitoramento_estado_conservacao = models.IntegerField(null=True)
    caneletas_ilhas_bombas_disponibilidade = models.NullBooleanField(null=True)
    caneletas_ilhas_bombas_estado_conservacao = models.IntegerField(null=True)
    caneletas_perimetro_disponibilidade = models.NullBooleanField(null=True)
    caneletas_perimetro_estado_conservacao = models.IntegerField(null=True)
    piso_concreto_alisado_disponibilidade = models.NullBooleanField(null=True)
    piso_concreto_alisado_estado_conservacao = models.IntegerField(null=True)
    caneletas_interligadas_sao_disponibilidade = models.NullBooleanField(null=True)
    caneletas_interligadas_sao_estado_conservacao = models.IntegerField(null=True)
    sistema_deteccao_vazamento_disponibilidade = models.NullBooleanField(null=True)
    sistema_deteccao_vazamento_estado_conservacao = models.IntegerField(null=True)

    area_lavagem_piso_can_sao_disponibilidade = models.NullBooleanField(null=True)
    area_lavagem_piso_can_sao_estado_conservacao = models.IntegerField(null=True)
    area_troca_oleo_piso_can_sao_disponibilidade = models.NullBooleanField(null=True)
    area_troca_oleo_piso_can_sao_estado_conservacao = models.IntegerField(null=True)
    area_armazenamento_residuos_coberta_piso_disponibilidade = models.NullBooleanField(null=True)
    area_armazenamento_residuos_coberta_piso_estado_conservacao = models.IntegerField(null=True)
    atendido_rede_publica_saneamento = models.NullBooleanField(null=True)
    quantidade_tanques = models.IntegerField(null=True)
    capacidade_armazenamento = models.IntegerField(default=0)

    houve_sinistro_ultimos_anos = models.NullBooleanField(null=True)
    prejuizo_estimativa = models.DecimalField(decimal_places=2, max_digits=20, null=True)
    data_sinistro = models.DateField(null=True)
    ocorrencia = models.CharField(max_length=300, null=True)

    endereco_pdf = models.CharField(max_length=500, null=True)

    def __str__(self):
        return self.posto.nome + ' - ' + self.numero_proposta


class Foto(models.Model):
    endereco = models.CharField(max_length=500)
    laudo = models.ForeignKey('Laudo', on_delete=models.CASCADE, default=None)
