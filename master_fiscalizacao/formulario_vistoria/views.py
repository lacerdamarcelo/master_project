from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Posto, Laudo, Foto
from user_management.models import PermissoesUsuario
from django.views.decorators.csrf import csrf_exempt
from master_fiscalizacao.settings import MEDIA_ROOT, LAUDOS_LIST_PAGE_SIZE, STATIC_URL
from datetime import datetime
from django.core.mail import EmailMessage
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.http import HttpResponse
from wsgiref.util import FileWrapper
import os
import time


def abrir_pdf(request, laudo):
    laudo_object = Laudo.objects.get(id=laudo)
    response = HttpResponse(FileWrapper(open(laudo_object.endereco_pdf, 'rb')), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=' + laudo_object.endereco_pdf.split('/')[-1]
    return response


estado_conservacao_dict_inv = {-1: 'Indisponível', 0: 'Precário', 1: 'Regular', 2: 'Bom'}


def assinar_laudo(request, laudo):
    laudo_object = Laudo.objects.get(id=laudo)

    story = []

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
    ptext = '<font size=16>LAUDO DE INSPEÇÃO PRELIMINAR LIP</font>'
    story.append(Paragraph(ptext, styles["Normal"]))
    story.append(Spacer(1, 12))

    ptext = '<font size=10>_______________________________________________________________________________</font>'
    story.append(Paragraph(ptext, styles["Normal"]))
    story.append(Spacer(1, 12))

    ptext = '<font size=10><b>Nome/Razão Social</b><br></br></font><font size=12>' + laudo_object.posto.nome + '</font>'
    story.append(Paragraph(ptext, styles["Normal"]))
    story.append(Spacer(1, 12))

    ptext = '<font size=10><b>CNPJ</b><br></br></font><font size=12>' + laudo_object.posto.cnpj + '</font>'
    story.append(Paragraph(ptext, styles["Normal"]))
    story.append(Spacer(1, 12))

    ptext = '<font size=10><b>Nome Fantasia</b><br></br></font><font size=12>' + laudo_object.posto.nome_fantasia + '</font>'
    story.append(Paragraph(ptext, styles["Normal"]))
    story.append(Spacer(1, 12))

    ptext = '<font size=10><b>N° Proposta</b><br></br></font><font size=12>' + laudo_object.numero_proposta + '</font>'
    story.append(Paragraph(ptext, styles["Normal"]))
    story.append(Spacer(1, 12))

    ptext = '<font size=10><b>Endereço do estabelecimento</b><br></br></font><font size=12>' + laudo_object.posto.endereco + '</font>'
    story.append(Paragraph(ptext, styles["Normal"]))
    story.append(Spacer(1, 12))

    ptext = '<font size=10>_______________________________________________________________________________</font>'
    story.append(Paragraph(ptext, styles["Normal"]))
    story.append(Spacer(1, 12))

    if laudo_object.registro_anp_definitivo is not None:
        registro_anp = 'Definitivo' if laudo_object.registro_anp_definitivo else 'Provisório'
    else:
        registro_anp = 'Inexistente'
    registro_anp_numero = laudo_object.registro_anp_numero
    registro_anp_data_expedicao = laudo_object.registro_anp_data_expedicao
    registro_anp_data_validade = laudo_object.registro_anp_data_validade

    if laudo_object.alvara_funcionamento_definitivo is not None:
        alvara_funcionamento = 'Definitivo' if laudo_object.alvara_funcionamento_definitivo else 'Provisório'
    else:
        alvara_funcionamento = 'Inexistente'
    alvara_funcionamento_numero = laudo_object.alvara_funcionamento_numero
    alvara_funcionamento_data_expedicao = laudo_object.alvara_funcionamento_data_expedicao
    alvara_funcionamento_data_validade = laudo_object.alvara_funcionamento_data_validade

    if laudo_object.licenca_ambiental is not None :
        if laudo_object.licenca_ambiental == 0:
            licenca_ambiental = 'LP'
        else:
            if laudo_object.licenca_ambiental == 1:
                licenca_ambiental = 'LI'
            else:
                if laudo_object.licenca_ambiental == 2:
                    licenca_ambiental = 'LO'
                else:
                    licenca_ambiental = 'Inexistente'
    else:
        licenca_ambiental = 'Inexistente'
    licenca_ambiental_numero = laudo_object.licenca_ambiental_numero
    licenca_ambiental_data_expedicao = laudo_object.licenca_ambiental_data_expedicao
    licenca_ambiental_data_validade = laudo_object.licenca_ambiental_data_validade

    if laudo_object.atestado_regularidade_ar_sim is not None:
        atestado_regularidade_ar_sim = 'Definitivo' if laudo_object.atestado_regularidade_ar_sim else 'Inexistente'
    else:
        atestado_regularidade_ar_sim = 'Inexistente'
    atestado_regularidade_ar_numero = laudo_object.atestado_regularidade_ar_numero
    atestado_regularidade_ar_data_expedicao = laudo_object.atestado_regularidade_ar_data_expedicao
    atestado_regularidade_ar_data_validade = laudo_object.atestado_regularidade_ar_data_validade

    data = [['Documento', 'Tipo', 'Número', 'Data da Expedição', 'Data da Validade'],
            ['Registro ANP', registro_anp, registro_anp_numero, registro_anp_data_expedicao, registro_anp_data_validade],
            ['Alvará de Funcionamento', alvara_funcionamento, alvara_funcionamento_numero, alvara_funcionamento_data_expedicao, alvara_funcionamento_data_validade],
            ['Licença Ambiental', licenca_ambiental, licenca_ambiental_numero, licenca_ambiental_data_expedicao, licenca_ambiental_data_validade],
            ['Atestado de Regularidade-AR', atestado_regularidade_ar_sim, atestado_regularidade_ar_numero, atestado_regularidade_ar_data_expedicao, atestado_regularidade_ar_data_validade]]

    table_style = TableStyle([('FONT', (0, 0), (4, 0), 'Helvetica-Bold')])
    t = Table(data, style=table_style)
    story.append(t)

    ptext = '<br></br><font size=10><b>Observação</b><br></br></font><font size=12>' + ('' if laudo_object.observacao is None else laudo_object.observacao) + '</font>'
    story.append(Paragraph(ptext, styles["Normal"]))
    story.append(Spacer(1, 12))

    ptext = '<font size=10>_______________________________________________________________________________</font>'
    story.append(Paragraph(ptext, styles["Normal"]))
    story.append(Spacer(1, 12))

    ptext = '<br></br><font size=12><b>Disponibilidade de Serviços</b><br></br></font>'
    story.append(Paragraph(ptext, styles["Normal"]))
    story.append(Spacer(1, 12))

    venda_combustiveis_disponivel = 'Sim' if laudo_object.venda_combustiveis_disponivel else 'Não'
    lavagem_viculos_disponivel = 'Sim' if laudo_object.lavagem_viculos_disponivel else 'Não'
    restaurante_lanchonete_conveniencia_disponivel = 'Sim' if laudo_object.restaurante_lanchonete_conveniencia_disponivel else 'Não'
    troca_oleo_disponivel = 'Sim' if laudo_object.troca_oleo_disponivel else 'Não'
    oficina_mecanica_disponivel = 'Sim' if laudo_object.oficina_mecanica_disponivel else 'Não'
    venda_gas_cozinha = 'Sim' if laudo_object.venda_gas_cozinha else 'Não'

    data = [['Serviço', 'Disponível'],
            ['Venda de Combustíveis', venda_combustiveis_disponivel],
            ['Lavagem de veículos', lavagem_viculos_disponivel],
            ['Restaurante / Lanchonete / Loja de conveniência', restaurante_lanchonete_conveniencia_disponivel],
            ['Troca de Óleo', troca_oleo_disponivel],
            ['Oficina Mecânica', oficina_mecanica_disponivel],
            ['Venda de gás de cozinha', venda_gas_cozinha]]

    table_style = TableStyle([('FONT', (0, 0), (1, 0), 'Helvetica-Bold')])
    t = Table(data, style=table_style)
    story.append(t)

    ptext = '<br></br><font size=10><b>Outros</b><br></br></font><font size=12>' + ('' if laudo_object.outros_servicos_disponibilidade is None else laudo_object.outros_servicos_disponibilidade) + '</font>'
    story.append(Paragraph(ptext, styles["Normal"]))
    story.append(Spacer(1, 12))

    ptext = '<font size=10>_______________________________________________________________________________</font>'
    story.append(Paragraph(ptext, styles["Normal"]))
    story.append(Spacer(1, 12))

    ptext = '<br></br><font size=12><b>Disponibilidade de Infraestrutura</b><br></br></font>'
    story.append(Paragraph(ptext, styles["Normal"]))
    story.append(Spacer(1, 12))

    valvula_retentora_vapor_disponibilidade = 'Sim' if laudo_object.valvula_retentora_vapor_disponibilidade else 'Não'
    poco_monitoramento_disponibilidade = 'Sim' if laudo_object.poco_monitoramento_disponibilidade else 'Não'
    caneletas_ilhas_bombas_disponibilidade = 'Sim' if laudo_object.caneletas_ilhas_bombas_disponibilidade else 'Não'
    caneletas_perimetro_disponibilidade = 'Sim' if laudo_object.caneletas_perimetro_disponibilidade else 'Não'
    piso_concreto_alisado_disponibilidade = 'Sim' if laudo_object.piso_concreto_alisado_disponibilidade else 'Não'
    caneletas_interligadas_sao_disponibilidade = 'Sim' if laudo_object.caneletas_interligadas_sao_disponibilidade else 'Não'
    sistema_deteccao_vazamento_disponibilidade = 'Sim' if laudo_object.sistema_deteccao_vazamento_disponibilidade else 'Não'
    area_lavagem_piso_can_sao_disponibilidade = 'Sim' if laudo_object.area_lavagem_piso_can_sao_disponibilidade else 'Não'
    area_troca_oleo_piso_can_sao_disponibilidade = 'Sim' if laudo_object.area_troca_oleo_piso_can_sao_disponibilidade else 'Não'
    area_armazenamento_residuos_coberta_piso_disponibilidade = 'Sim' if laudo_object.area_armazenamento_residuos_coberta_piso_disponibilidade else 'Não'
    atendido_rede_publica_saneamento = 'Sim' if laudo_object.atendido_rede_publica_saneamento else 'Não'

    data = [['Item', 'Disponível', 'Estado de conservação'],
            ['Válvula retentora de vapor', valvula_retentora_vapor_disponibilidade, estado_conservacao_dict_inv[laudo_object.valvula_retentora_vapor_estado_conservacao]],
            ['Poço de monitoramento', poco_monitoramento_disponibilidade, estado_conservacao_dict_inv[laudo_object.poco_monitoramento_estado_conservacao]],
            ['Caneletas de ilha de bombas', caneletas_ilhas_bombas_disponibilidade, estado_conservacao_dict_inv[laudo_object.caneletas_ilhas_bombas_estado_conservacao]],
            ['Caneletas de perímetro', caneletas_perimetro_disponibilidade, estado_conservacao_dict_inv[laudo_object.caneletas_perimetro_estado_conservacao]],
            ['Piso em concreto alisado na pista de bombas', piso_concreto_alisado_disponibilidade, estado_conservacao_dict_inv[laudo_object.piso_concreto_alisado_estado_conservacao]],
            ['Canaletas interligadas ao SAO', caneletas_interligadas_sao_disponibilidade, estado_conservacao_dict_inv[laudo_object.caneletas_interligadas_sao_estado_conservacao]],
            ['Possui sistema de detecção de vazamentos', sistema_deteccao_vazamento_disponibilidade, estado_conservacao_dict_inv[laudo_object.sistema_deteccao_vazamento_estado_conservacao]],
            ['Área de lavagem de veículos com piso, canaletas e SAO', area_lavagem_piso_can_sao_disponibilidade, estado_conservacao_dict_inv[laudo_object.area_lavagem_piso_can_sao_estado_conservacao]],
            ['Área de troca de óleo com piso, canaletas e SAO', area_troca_oleo_piso_can_sao_disponibilidade, estado_conservacao_dict_inv[laudo_object.area_troca_oleo_piso_can_sao_estado_conservacao]],
            ['Área de armazenamento de resíduos coberta com piso', area_armazenamento_residuos_coberta_piso_disponibilidade, estado_conservacao_dict_inv[laudo_object.area_armazenamento_residuos_coberta_piso_estado_conservacao]]]

    table_style = TableStyle([('FONT', (0, 0), (2, 0), 'Helvetica-Bold')])
    t = Table(data, style=table_style)
    story.append(t)

    tanque_sub_parede_dupla_jaquetado = 'Disponível' if laudo_object.tanque_sub_parede_dupla_jaquetado else 'Indisponível'

    ptext = '<br></br><font size=10><b>Tanque subterrâneo parede dupla jaquetado (NBR 13.785 da ABNT): </b></font><font size=10>' + tanque_sub_parede_dupla_jaquetado + '</font>'
    story.append(Paragraph(ptext, styles["Normal"]))
    story.append(Spacer(1, 12))

    ptext = '<font size=10><b>Data da instalação do tanque subterrâneo de parede dupla jaquetado: </b></font><font size=10>' + (str(laudo_object.tanque_sub_parede_data_instalacao) if laudo_object.tanque_sub_parede_data_instalacao is not None else 'Indisponível') + '</font>'
    story.append(Paragraph(ptext, styles["Normal"]))
    story.append(Spacer(1, 12))

    ptext = '<font size=10><b>Atendido pela rede pública de saneamento? </b></font><font size=10>' + atendido_rede_publica_saneamento + '</font>'
    story.append(Paragraph(ptext, styles["Normal"]))
    story.append(Spacer(1, 12))

    ptext = '<font size=10><b>Quantidade de tanques (unidade): </b></font><font size=10>' + str(laudo_object.quantidade_tanques) + '</font>'
    story.append(Paragraph(ptext, styles["Normal"]))
    story.append(Spacer(1, 12))

    ptext = '<font size=10><b>Capacidade total de armazenamento (litros): </b></font><font size=10>' + str(laudo_object.capacidade_armazenamento) + '</font>'
    story.append(Paragraph(ptext, styles["Normal"]))
    story.append(Spacer(1, 12))


    ptext = '<font size=10>_______________________________________________________________________________</font>'
    story.append(Paragraph(ptext, styles["Normal"]))
    story.append(Spacer(1, 12))

    ptext = '<br></br><font size=10><b>Houve algum sinistro nos cinco últimos anos?</b><br></br></font><font size=12>' + ('Sim' if laudo_object.outros_servicos_disponibilidade else 'Não') + '</font>'
    story.append(Paragraph(ptext, styles["Normal"]))
    story.append(Spacer(1, 12))

    ptext = '<br></br><font size=10><b>Prejuízo, estimativa R$</b><br></br></font><font size=12>' + str(laudo_object.prejuizo_estimativa) + '</font>'
    story.append(Paragraph(ptext, styles["Normal"]))
    story.append(Spacer(1, 12))

    ptext = '<br></br><font size=10><b>Data</b><br></br></font><font size=12>' + (str(laudo_object.data_sinistro) if laudo_object.data_sinistro is not None else '') + '</font>'
    story.append(Paragraph(ptext, styles["Normal"]))
    story.append(Spacer(1, 12))

    ptext = '<br></br><font size=10><b>Ocorrência</b><br></br></font><font size=12>' + laudo_object.ocorrencia + '</font>'
    story.append(Paragraph(ptext, styles["Normal"]))
    story.append(Spacer(1, 12))

    ptext = '<font size=10>_______________________________________________________________________________</font>'
    story.append(Paragraph(ptext, styles["Normal"]))
    story.append(Spacer(1, 12))

    ptext = '<br></br><font size=12><b>PARECER TÉCNICO</b><br></br></font>'
    story.append(Paragraph(ptext, styles["Normal"]))
    story.append(Spacer(1, 12))

    radio_reg_anp = laudo_object.registro_anp_definitivo
    radio_alv_func = laudo_object.alvara_funcionamento_definitivo
    radio_lic_amb = laudo_object.licenca_ambiental
    radio_atest_reg = laudo_object.atestado_regularidade_ar_sim
    serv_venda_comb = 'checked' if laudo_object.venda_combustiveis_disponivel else ''
    serv_lav_veiculos = 'checked' if laudo_object.lavagem_viculos_disponivel else ''
    serv_lanc_conven = 'checked' if laudo_object.restaurante_lanchonete_conveniencia_disponivel else ''
    serv_troca_oleo = 'checked' if laudo_object.troca_oleo_disponivel else ''
    valv_ret_vap = 'checked' if laudo_object.valvula_retentora_vapor_disponibilidade else ''
    tanq_sub_par_dup_jaq = 'checked' if laudo_object.tanque_sub_parede_dupla_jaquetado else ''
    poco_mon = 'checked' if laudo_object.poco_monitoramento_disponibilidade else ''
    can_ilha_bom = 'checked' if laudo_object.caneletas_ilhas_bombas_disponibilidade else ''
    can_per = 'checked' if laudo_object.caneletas_perimetro_disponibilidade else ''
    piso_alisado_bombas = 'checked' if laudo_object.piso_concreto_alisado_disponibilidade else ''
    can_int_sao = 'checked' if laudo_object.caneletas_interligadas_sao_disponibilidade else ''
    sist_det_vaz = 'checked' if laudo_object.sistema_deteccao_vazamento_disponibilidade else ''
    lav_vei_piso_can_sao = 'checked' if laudo_object.area_lavagem_piso_can_sao_disponibilidade else ''
    area_oleo_piso = 'checked' if laudo_object.area_troca_oleo_piso_can_sao_disponibilidade else ''
    area_res_piso = 'checked' if laudo_object.area_armazenamento_residuos_coberta_piso_disponibilidade else ''

    atendimento_req_tecnicos = [radio_reg_anp, radio_alv_func, str(radio_lic_amb),
                                radio_atest_reg,
                                serv_venda_comb, serv_lav_veiculos,
                                serv_troca_oleo, valv_ret_vap,
                                tanq_sub_par_dup_jaq, poco_mon, can_ilha_bom,
                                can_per, piso_alisado_bombas, can_int_sao,
                                sist_det_vaz, area_res_piso]

    if serv_lav_veiculos == 'checked':
        atendimento_req_tecnicos.append(lav_vei_piso_can_sao)
    if serv_troca_oleo == 'checked':
        atendimento_req_tecnicos.append(area_oleo_piso)

    percentual_req_tecnicos = float(atendimento_req_tecnicos.count('checked'))
    percentual_req_tecnicos += float(atendimento_req_tecnicos.count(True))
    percentual_req_tecnicos += float(atendimento_req_tecnicos.count(False))
    if radio_atest_reg is False:
        percentual_req_tecnicos -= 1
    percentual_req_tecnicos += float(atendimento_req_tecnicos.count('0'))
    percentual_req_tecnicos += float(atendimento_req_tecnicos.count('1'))
    percentual_req_tecnicos += float(atendimento_req_tecnicos.count('2'))
    percentual_req_tecnicos /= len(atendimento_req_tecnicos)

    ptext = '<br></br><font size=10><b>ATENDIMENTO AOS REQUISITOS TÉCNICOS: </b></font><font size=10>' + str(float(int(percentual_req_tecnicos * 1000)) / 10) + '%</font>'
    story.append(Paragraph(ptext, styles["Normal"]))
    story.append(Spacer(1, 12))

    parecer_tecnico = ''
    enquadramento = ''
    if percentual_req_tecnicos <= 1.0 and percentual_req_tecnicos >= 0.86:
        parecer_tecnico = 'Conforme as externalidades ambientais evidenciadas in loco e registro fotográfico, o estabelecimeto apresentou instalações que atenderam plenamente as normas relativas a IN no005/2006 CPRH e NBR 13785.'
        enquadramento = 'A1'
    else:
        if percentual_req_tecnicos <= 0.85 and percentual_req_tecnicos >= 0.61:
            parecer_tecnico = 'Considerando as informações coletadas em vistoria in loco e registro fotográfico, o estabelecimento cumpriu satisfatoriamente os requisitos definidos pelas normativas IN no005/2006 CPRH e NBR 13785, restando a adoção de algumas medidas para o pleno atendimento.'
            enquadramento = 'A2'
        else:
            if percentual_req_tecnicos <= 0.6 and percentual_req_tecnicos >= 0.46:
                parecer_tecnico = 'A partir de vistoria in loco registrada pelas fotos, o estabelecimento atendeu minimamnte as condições estabelecidas na IN no005/2006 CPRH e NBR 13785, devendo o estabelecimento demonstrar o cumprimento das exigências na norma supracitada para solucionar tais deficiências.'
                enquadramento = 'B1'
            else:
                if percentual_req_tecnicos <= 0.45 and percentual_req_tecnicos >= 0.26:
                    parecer_tecnico = 'Em vistoria realizada in loco , foram constatadas algumas não conformidades frente às normas vigentes IN no005/2006 e NBR 13785 relativas a atividade em questão, sendo portanto necessária a busca por soluções urgentes para saná-las e possar a atender os requisitos legais que regram o funcionamento do estabelecimento.'
                    enquadramento = 'B2'
                else:
                    parecer_tecnico = 'Após análise das informações registradas na visita técnica com registro fotográfico, foram constatadas não conformidades no que concerne ao atendimento dos requisitos da IN no005/2006 e NBR 13785, apresentando condições desfavoráveis para seu funcionamento, sendo necessária interveções físicas para dotá-la minimamente das infraestruturas de proteção e segurança.'
                    enquadramento = 'C'

    ptext = '<br></br><font size=10>' + parecer_tecnico + '</font>'
    story.append(Paragraph(ptext, styles["Normal"]))
    story.append(Spacer(1, 12))

    ptext = '<br></br><font size=10><b>Enquadramento: </b></font><font size=10>' + enquadramento + '</font>'
    story.append(Paragraph(ptext, styles["Normal"]))
    story.append(Spacer(1, 12))

    post_data = request.POST
    ressalvas = post_data.get('ressalvas', 'Nenhuma')

    ptext = '<br></br><font size=10><b>Ressalvas</b><br></br></font><font size=10>' + ressalvas + '</font>'
    story.append(Paragraph(ptext, styles["Normal"]))
    story.append(Spacer(1, 12))

    ptext = '<font size=10>_______________________________________________________________________________</font>'
    story.append(Paragraph(ptext, styles["Normal"]))
    story.append(Spacer(1, 12))

    formatted_time = time.ctime()

    ptext = '<br></br><font size=10><b>Data e Hora: </b></font><font size=10>' + str(formatted_time) + '</font>'
    story.append(Paragraph(ptext, styles["Normal"]))
    story.append(Spacer(1, 12))

    ptext = '<br></br><font size=10><b>Empresa especializada:</b><br></br></font>'
    story.append(Paragraph(ptext, styles["Normal"]))
    story.append(Spacer(1, 12))

    logo = "formulario_vistoria/static/media/master_logo.jpg"
    im = Image(logo)
    story.append(im)

    ptext = '<font size=10>_______________________________________________________________________________</font>'
    story.append(Paragraph(ptext, styles["Normal"]))
    story.append(Spacer(1, 12))

    ptext = '<br></br><font size=10><b>ANEXOS</b><br></br></font>'
    story.append(Paragraph(ptext, styles["Normal"]))
    story.append(Spacer(1, 12))

    fotos = Foto.objects.filter(laudo=laudo_object)

    for foto in fotos:
        logo = foto.endereco
        im = Image(logo)
        story.append(im)

    ptext = '<font size=10>_______________________________________________________________________________</font>'
    story.append(Paragraph(ptext, styles["Normal"]))
    story.append(Spacer(1, 12))
    time_str = str(time.time())
    nome_posto = laudo_object.posto.nome.replace(' ', '_')

    doc = SimpleDocTemplate("formulario_vistoria/laudos/laudo_" + nome_posto + str(laudo_object.id) + time_str.replace('.', '') + ".pdf")

    doc.build(story)

    enviar_email_laudo(laudo_object.posto.nome, 'formulario_vistoria/laudos/laudo_' + nome_posto + str(laudo_object.id) + time_str.replace('.', '') + '.pdf', laudo_object.usuario)
    laudo_object.status = 1
    laudo_object.data_permissao = datetime.now()
    laudo_object.endereco_pdf = 'formulario_vistoria/laudos/laudo_' + nome_posto + str(laudo_object.id) + time_str.replace('.', '') + '.pdf'
    laudo_object.save()
    return redirect('/formulario_vistoria/index/1')


def enviar_email_laudo(nome_posto, file_path, user):
    texto = 'Caro cliente,\n\nSegue em anexo o laudo da última vistoria realizada\n'
    texto += 'no estabelecimento ' + nome_posto + '.'
    file = open(file_path, 'rb')
    mail = EmailMessage('[Sistema de Vistoria Master] Novo Laudo emitido',
                        texto, to=[user.email])
    mail.attach(file_path, file.read(), 'application/pdf')
    mail.send()
    file.close()


def save_solicitacao_vistoria(request):
    post_data = request.POST
    postos = Posto.objects.order_by('nome')
    posto_id = post_data.get('id_posto', None)
    numero_proposta = post_data.get('input_num_proposta', None)
    invalid_fields = []
    is_valid_data = True
    if posto_id is None:
        invalid_fields.append('id_posto')
        is_valid_data = False
    if numero_proposta is None:
        invalid_fields.append('input_num_proposta')
        is_valid_data = False
    if is_valid_data:
        selected_posto = Posto.objects.get(id=posto_id)
        data_criacao = datetime.now()
        laudo = Laudo(status=3,
                      data_criacao=data_criacao,
                      usuario=User.objects.get(id=request.user.id),
                      posto=selected_posto, numero_proposta=numero_proposta)
        context = {'first_name': request.user.first_name,
                   'last_name': request.user.last_name,
                   'show_empty_data': True}
        laudo.save()
        enviar_email_solicitacao_vistoria()
        return redirect('/formulario_vistoria/index/registration_confirm/1', context)
    else:
        context = {}
        context['numero_proposta'] = numero_proposta if numero_proposta is not None else ''
        context['invalid_fields'] = invalid_fields
        context['first_name'] = request.user.first_name
        context['last_name'] = request.user.last_name
        context['selected_posto'] = selected_posto
        context['postos'] = postos
        context['invalid_form'] = True
        return render(request, 'formulario_vistoria/solicitacao_vistoria.html', context)


def enviar_email_solicitacao_vistoria():
    texto = 'Olá!\n\nVocê tem uma nova solicitação de vistoria no Sistema de '
    texto += 'Vistorias Master. Clique no link abaixo para acessar o sistema.\n'
    texto += '\nhttp://' + os.environ['HOST_IP_PORT'] + '/login'
    mail = EmailMessage('[Sistema de Vistoria Master] Nova solicitação de vistoria',
                        texto, to=[os.environ['EMAIL_SOLICITACOES_VISTORIAS']])
    mail.send()


def solicitacao_vistoria(request):
    if request.user.is_authenticated():
        postos = Posto.objects.order_by('nome')
        context = {'postos': postos, 'first_name': request.user.first_name, 'last_name': request.user.last_name, 'just_viewing_form': False}
        return render(request, 'formulario_vistoria/solicitacao_vistoria.html', context)
    else:
        return redirect('/login/')


def cadastro_posto(request):
    context = {'gmaps_key': os.environ['GMAPS_KEY']}
    return render(request, 'formulario_vistoria/cadastro_posto.html', context)


def load_laudo_data(laudo, disabled_fields, just_viewing_form):
    laudo = Laudo.objects.get(id=laudo)
    status = laudo.status
    selected_posto = laudo.posto
    postos = Posto.objects.order_by('nome')
    numero_proposta = laudo.numero_proposta
    radio_reg_anp = laudo.registro_anp_definitivo
    reg_anp_num = laudo.registro_anp_numero if laudo.registro_anp_numero is not None else ''
    registro_anp_data_expedicao = laudo.registro_anp_data_expedicao
    if registro_anp_data_expedicao is not None:
        registro_anp_data_expedicao = str(registro_anp_data_expedicao.year) + '-' + str(registro_anp_data_expedicao.month) + '-' + str(registro_anp_data_expedicao.day)
    registro_anp_validade = laudo.registro_anp_data_validade
    if registro_anp_data_expedicao is not None:
        registro_anp_validade = str(registro_anp_validade.year) + '-' + str(registro_anp_validade.month) + '-' + str(registro_anp_validade.day)
    radio_alv_func = laudo.alvara_funcionamento_definitivo
    alv_func_num = laudo.alvara_funcionamento_numero if laudo.alvara_funcionamento_numero is not None else ''
    alv_func_data_expedicao = laudo.alvara_funcionamento_data_expedicao
    if alv_func_data_expedicao is not None:
        alv_func_data_expedicao = str(alv_func_data_expedicao.year) + '-' + str(alv_func_data_expedicao.month) + '-' + str(alv_func_data_expedicao.day)
    alv_func_validade = laudo.alvara_funcionamento_data_validade
    if alv_func_validade is not None:
        alv_func_validade = str(alv_func_validade.year) + '-' + str(alv_func_validade.month) + '-' + str(alv_func_validade.day)
    radio_lic_amb = laudo.licenca_ambiental
    lic_amb_num = laudo.licenca_ambiental_numero if laudo.licenca_ambiental_numero is not None else ''
    lic_amb_data_expedicao = laudo.licenca_ambiental_data_expedicao
    if lic_amb_data_expedicao is not None:
        lic_amb_data_expedicao = str(lic_amb_data_expedicao.year) + '-' + str(lic_amb_data_expedicao.month) + '-' + str(lic_amb_data_expedicao.day)
    lic_amb_validade = laudo.licenca_ambiental_data_validade
    if lic_amb_validade is not None:
        lic_amb_validade = str(lic_amb_validade.year) + '-' + str(lic_amb_validade.month) + '-' + str(lic_amb_validade.day)
    radio_atest_reg = laudo.atestado_regularidade_ar_sim
    atest_reg_num = laudo.atestado_regularidade_ar_numero if laudo.atestado_regularidade_ar_numero is not None else ''
    atest_reg_data_expedicao = laudo.atestado_regularidade_ar_data_expedicao
    if atest_reg_data_expedicao is not None:
        atest_reg_data_expedicao = str(atest_reg_data_expedicao.year) + '-' + str(atest_reg_data_expedicao.month) + '-' + str(atest_reg_data_expedicao.day)
    atest_reg_validade = laudo.atestado_regularidade_ar_data_validade
    if atest_reg_validade is not None:
        atest_reg_validade = str(atest_reg_validade.year) + '-' + str(atest_reg_validade.month) + '-' + str(atest_reg_validade.day)
    observacao = laudo.observacao if laudo.observacao is not None else ''
    serv_venda_comb = 'checked' if laudo.venda_combustiveis_disponivel else ''
    serv_lav_veiculos = 'checked' if laudo.lavagem_viculos_disponivel else ''
    serv_lanc_conven = 'checked' if laudo.restaurante_lanchonete_conveniencia_disponivel else ''
    serv_troca_oleo = 'checked' if laudo.troca_oleo_disponivel else ''
    serv_ofic_mec = 'checked' if laudo.oficina_mecanica_disponivel else ''
    serv_gas_cozinha = 'checked' if laudo.venda_gas_cozinha else ''
    outros_servicos = laudo.outros_servicos_disponibilidade if laudo.outros_servicos_disponibilidade is not None else ''
    valv_ret_vap = 'checked' if laudo.valvula_retentora_vapor_disponibilidade else ''
    radio_val_ret_vap_0 = 'checked' if laudo.valvula_retentora_vapor_estado_conservacao == -1 else ''
    radio_val_ret_vap_1 = 'checked' if laudo.valvula_retentora_vapor_estado_conservacao == 2 else ''
    radio_val_ret_vap_2 = 'checked' if laudo.valvula_retentora_vapor_estado_conservacao == 1 else ''
    radio_val_ret_vap_3 = 'checked' if laudo.valvula_retentora_vapor_estado_conservacao == 0 else ''
    tanq_sub_par_dup_jaq = 'checked' if laudo.tanque_sub_parede_dupla_jaquetado else ''
    tanq_sub_par_dup_jaq_data_inst = laudo.tanque_sub_parede_data_instalacao
    if tanq_sub_par_dup_jaq_data_inst is not None:
        tanq_sub_par_dup_jaq_data_inst = str(tanq_sub_par_dup_jaq_data_inst.year) + '-' + str(tanq_sub_par_dup_jaq_data_inst.month) + '-' + str(tanq_sub_par_dup_jaq_data_inst.day)
    poco_mon = 'checked' if laudo.poco_monitoramento_disponibilidade else ''
    radio_poco_mon_0 = 'checked' if laudo.poco_monitoramento_estado_conservacao == -1 else ''
    radio_poco_mon_1 = 'checked' if laudo.poco_monitoramento_estado_conservacao == 2 else ''
    radio_poco_mon_2 = 'checked' if laudo.poco_monitoramento_estado_conservacao == 1 else ''
    radio_poco_mon_3 = 'checked' if laudo.poco_monitoramento_estado_conservacao == 0 else ''
    can_ilha_bom = 'checked' if laudo.caneletas_ilhas_bombas_disponibilidade else ''
    radio_can_ilha_bom_0 = 'checked' if laudo.caneletas_ilhas_bombas_estado_conservacao == -1 else ''
    radio_can_ilha_bom_1 = 'checked' if laudo.caneletas_ilhas_bombas_estado_conservacao == 2 else ''
    radio_can_ilha_bom_2 = 'checked' if laudo.caneletas_ilhas_bombas_estado_conservacao == 1 else ''
    radio_can_ilha_bom_3 = 'checked' if laudo.caneletas_ilhas_bombas_estado_conservacao == 0 else ''
    can_per = 'checked' if laudo.caneletas_perimetro_disponibilidade else ''
    radio_can_per_0 = 'checked' if laudo.caneletas_perimetro_estado_conservacao == -1 else ''
    radio_can_per_1 = 'checked' if laudo.caneletas_perimetro_estado_conservacao == 2 else ''
    radio_can_per_2 = 'checked' if laudo.caneletas_perimetro_estado_conservacao == 1 else ''
    radio_can_per_3 = 'checked' if laudo.caneletas_perimetro_estado_conservacao == 0 else ''
    piso_alisado_bombas = 'checked' if laudo.piso_concreto_alisado_disponibilidade else ''
    radio_piso_alisado_bombas_0 = 'checked' if laudo.piso_concreto_alisado_estado_conservacao == -1 else ''
    radio_piso_alisado_bombas_1 = 'checked' if laudo.piso_concreto_alisado_estado_conservacao == 2 else ''
    radio_piso_alisado_bombas_2 = 'checked' if laudo.piso_concreto_alisado_estado_conservacao == 1 else ''
    radio_piso_alisado_bombas_3 = 'checked' if laudo.piso_concreto_alisado_estado_conservacao == 0 else ''
    can_int_sao = 'checked' if laudo.caneletas_interligadas_sao_disponibilidade else ''
    radio_can_int_sao_0 = 'checked' if laudo.caneletas_interligadas_sao_estado_conservacao == -1 else ''
    radio_can_int_sao_1 = 'checked' if laudo.caneletas_interligadas_sao_estado_conservacao == 2 else ''
    radio_can_int_sao_2 = 'checked' if laudo.caneletas_interligadas_sao_estado_conservacao == 1 else ''
    radio_can_int_sao_3 = 'checked' if laudo.caneletas_interligadas_sao_estado_conservacao == 0 else ''
    sist_det_vaz = 'checked' if laudo.sistema_deteccao_vazamento_disponibilidade else ''
    radio_sist_det_vaz_0 = 'checked' if laudo.sistema_deteccao_vazamento_estado_conservacao == -1 else ''
    radio_sist_det_vaz_1 = 'checked' if laudo.sistema_deteccao_vazamento_estado_conservacao == 2 else ''
    radio_sist_det_vaz_2 = 'checked' if laudo.sistema_deteccao_vazamento_estado_conservacao == 1 else ''
    radio_sist_det_vaz_3 = 'checked' if laudo.sistema_deteccao_vazamento_estado_conservacao == 0 else ''
    lav_vei_piso_can_sao = 'checked' if laudo.area_lavagem_piso_can_sao_disponibilidade else ''
    radio_lav_vei_piso_can_sao_0 = 'checked' if laudo.area_lavagem_piso_can_sao_estado_conservacao == -1 else ''
    radio_lav_vei_piso_can_sao_1 = 'checked' if laudo.area_lavagem_piso_can_sao_estado_conservacao == 2 else ''
    radio_lav_vei_piso_can_sao_2 = 'checked' if laudo.area_lavagem_piso_can_sao_estado_conservacao == 1 else ''
    radio_lav_vei_piso_can_sao_3 = 'checked' if laudo.area_lavagem_piso_can_sao_estado_conservacao == 0 else ''
    area_oleo_piso = 'checked' if laudo.area_troca_oleo_piso_can_sao_disponibilidade else ''
    radio_area_oleo_piso_0 = 'checked' if laudo.area_troca_oleo_piso_can_sao_estado_conservacao == -1 else ''
    radio_area_oleo_piso_1 = 'checked' if laudo.area_troca_oleo_piso_can_sao_estado_conservacao == 2 else ''
    radio_area_oleo_piso_2 = 'checked' if laudo.area_troca_oleo_piso_can_sao_estado_conservacao == 1 else ''
    radio_area_oleo_piso_3 = 'checked' if laudo.area_troca_oleo_piso_can_sao_estado_conservacao == 0 else ''
    area_res_piso = 'checked' if laudo.area_armazenamento_residuos_coberta_piso_disponibilidade else ''
    radio_area_res_piso_0 = 'checked' if laudo.area_armazenamento_residuos_coberta_piso_estado_conservacao == -1 else ''
    radio_area_res_piso_1 = 'checked' if laudo.area_armazenamento_residuos_coberta_piso_estado_conservacao == 2 else ''
    radio_area_res_piso_2 = 'checked' if laudo.area_armazenamento_residuos_coberta_piso_estado_conservacao == 1 else ''
    radio_area_res_piso_3 = 'checked' if laudo.area_armazenamento_residuos_coberta_piso_estado_conservacao == 0 else ''
    at_red_pub_san = 'checked' if laudo.atendido_rede_publica_saneamento else ''
    quant_tanq_uni_select_1 = 'selected' if laudo.quantidade_tanques == 1 else ''
    quant_tanq_uni_select_2 = 'selected' if laudo.quantidade_tanques == 2 else ''
    quant_tanq_uni_select_3 = 'selected' if laudo.quantidade_tanques == 3 else ''
    quant_tanq_uni_select_4 = 'selected' if laudo.quantidade_tanques == 4 else ''
    quant_tanq_uni_select_5 = 'selected' if laudo.quantidade_tanques == 5 else ''
    quant_tanq_uni_select_6 = 'selected' if laudo.quantidade_tanques == 6 else ''
    quant_tanq_uni_select_7 = 'selected' if laudo.quantidade_tanques == 7 else ''
    quant_tanq_uni_select_8 = 'selected' if laudo.quantidade_tanques == 8 else ''
    quant_tanq_uni_select_9 = 'selected' if laudo.quantidade_tanques == 9 else ''
    quant_tanq_uni_select_10 = 'selected' if laudo.quantidade_tanques == 10 else ''
    cap_tot_arm_txt = laudo.capacidade_armazenamento
    houve_sinistro = 'checked' if laudo.houve_sinistro_ultimos_anos else ''
    prej_estim = laudo.prejuizo_estimativa if laudo.prejuizo_estimativa is not None else ''
    sinistro_data = laudo.data_sinistro
    if sinistro_data is not None:
        sinistro_data = str(sinistro_data.year) + '-' + str(sinistro_data.month) + '-' + str(sinistro_data.day)
    ocorrencia_text = laudo.ocorrencia if laudo.ocorrencia is not None else ''

    fotos_entries = Foto.objects.filter(laudo=laudo)
    fotos = []
    for i in range(0, len(fotos_entries)):
        fotos.append(fotos_entries[i].endereco.split('/site_media/')[1])

    atendimento_req_tecnicos = [radio_reg_anp, radio_alv_func, str(radio_lic_amb),
                                radio_atest_reg,
                                serv_venda_comb, serv_lav_veiculos,
                                serv_troca_oleo, valv_ret_vap,
                                tanq_sub_par_dup_jaq, poco_mon, can_ilha_bom,
                                can_per, piso_alisado_bombas, can_int_sao,
                                sist_det_vaz, area_res_piso]

    if serv_lav_veiculos == 'checked':
        atendimento_req_tecnicos.append(lav_vei_piso_can_sao)
    if serv_troca_oleo == 'checked':
        atendimento_req_tecnicos.append(area_oleo_piso)

    percentual_req_tecnicos = float(atendimento_req_tecnicos.count('checked'))
    percentual_req_tecnicos += float(atendimento_req_tecnicos.count(True))
    percentual_req_tecnicos += float(atendimento_req_tecnicos.count(False))
    if radio_atest_reg is False:
        percentual_req_tecnicos -= 1
    percentual_req_tecnicos += float(atendimento_req_tecnicos.count('0'))
    percentual_req_tecnicos += float(atendimento_req_tecnicos.count('1'))
    percentual_req_tecnicos += float(atendimento_req_tecnicos.count('2'))
    percentual_req_tecnicos /= len(atendimento_req_tecnicos)

    context = {'laudo_object': laudo,
               'selected_posto': selected_posto,
               'postos': postos,
               'numero_proposta': numero_proposta,
               'radio_reg_anp': radio_reg_anp,
               'reg_anp_num': reg_anp_num,
               'registro_anp_data_expedicao': registro_anp_data_expedicao,
               'registro_anp_validade': registro_anp_validade,
               'radio_alv_func': radio_alv_func,
               'alv_func_num': alv_func_num,
               'alv_func_data_expedicao': alv_func_data_expedicao,
               'alv_func_validade': alv_func_validade,
               'radio_lic_amb': radio_lic_amb,
               'lic_amb_num': lic_amb_num,
               'lic_amb_data_expedicao': lic_amb_data_expedicao,
               'lic_amb_validade': lic_amb_validade,
               'radio_atest_reg': radio_atest_reg,
               'atest_reg_num': atest_reg_num,
               'atest_reg_data_expedicao': atest_reg_data_expedicao,
               'atest_reg_validade': atest_reg_validade,
               'observacao': observacao,
               'serv_venda_comb': serv_venda_comb,
               'serv_lav_veiculos': serv_lav_veiculos,
               'serv_lanc_conven': serv_lanc_conven,
               'serv_troca_oleo': serv_troca_oleo,
               'serv_ofic_mec': serv_ofic_mec,
               'serv_gas_cozinha': serv_gas_cozinha,
               'outros_servicos': outros_servicos,
               'valv_ret_vap': valv_ret_vap,
               'radio_val_ret_vap_0': radio_val_ret_vap_0,
               'radio_val_ret_vap_1': radio_val_ret_vap_1,
               'radio_val_ret_vap_2': radio_val_ret_vap_2,
               'radio_val_ret_vap_3': radio_val_ret_vap_3,
               'tanq_sub_par_dup_jaq': tanq_sub_par_dup_jaq,
               'tanq_sub_par_dup_jaq_data_inst': tanq_sub_par_dup_jaq_data_inst,
               'poco_mon': poco_mon,
               'radio_poco_mon_0': radio_poco_mon_0,
               'radio_poco_mon_1': radio_poco_mon_1,
               'radio_poco_mon_2': radio_poco_mon_2,
               'radio_poco_mon_3': radio_poco_mon_3,
               'can_ilha_bom': can_ilha_bom,
               'radio_can_ilha_bom_0': radio_can_ilha_bom_0,
               'radio_can_ilha_bom_1': radio_can_ilha_bom_1,
               'radio_can_ilha_bom_2': radio_can_ilha_bom_2,
               'radio_can_ilha_bom_3': radio_can_ilha_bom_3,
               'can_per': can_per,
               'radio_can_per_0': radio_can_per_0,
               'radio_can_per_1': radio_can_per_1,
               'radio_can_per_2': radio_can_per_2,
               'radio_can_per_3': radio_can_per_3,
               'piso_alisado_bombas': piso_alisado_bombas,
               'radio_piso_alisado_bombas_0': radio_piso_alisado_bombas_0,
               'radio_piso_alisado_bombas_1': radio_piso_alisado_bombas_1,
               'radio_piso_alisado_bombas_2': radio_piso_alisado_bombas_2,
               'radio_piso_alisado_bombas_3': radio_piso_alisado_bombas_3,
               'can_int_sao': can_int_sao,
               'radio_can_int_sao_0': radio_can_int_sao_0,
               'radio_can_int_sao_1': radio_can_int_sao_1,
               'radio_can_int_sao_2': radio_can_int_sao_2,
               'radio_can_int_sao_3': radio_can_int_sao_3,
               'sist_det_vaz': sist_det_vaz,
               'radio_sist_det_vaz_0': radio_sist_det_vaz_0,
               'radio_sist_det_vaz_1': radio_sist_det_vaz_1,
               'radio_sist_det_vaz_2': radio_sist_det_vaz_2,
               'radio_sist_det_vaz_3': radio_sist_det_vaz_3,
               'lav_vei_piso_can_sao': lav_vei_piso_can_sao,
               'radio_lav_vei_piso_can_sao_0': radio_lav_vei_piso_can_sao_0,
               'radio_lav_vei_piso_can_sao_1': radio_lav_vei_piso_can_sao_1,
               'radio_lav_vei_piso_can_sao_2': radio_lav_vei_piso_can_sao_2,
               'radio_lav_vei_piso_can_sao_3': radio_lav_vei_piso_can_sao_3,
               'area_oleo_piso': area_oleo_piso,
               'radio_area_oleo_piso_0': radio_area_oleo_piso_0,
               'radio_area_oleo_piso_1': radio_area_oleo_piso_1,
               'radio_area_oleo_piso_2': radio_area_oleo_piso_2,
               'radio_area_oleo_piso_3': radio_area_oleo_piso_3,
               'area_res_piso': area_res_piso,
               'radio_area_res_piso_0': radio_area_res_piso_0,
               'radio_area_res_piso_1': radio_area_res_piso_1,
               'radio_area_res_piso_2': radio_area_res_piso_2,
               'radio_area_res_piso_3': radio_area_res_piso_3,
               'at_red_pub_san': at_red_pub_san,
               'quant_tanq_uni_select_1': quant_tanq_uni_select_1,
               'quant_tanq_uni_select_2': quant_tanq_uni_select_2,
               'quant_tanq_uni_select_3': quant_tanq_uni_select_3,
               'quant_tanq_uni_select_4': quant_tanq_uni_select_4,
               'quant_tanq_uni_select_5': quant_tanq_uni_select_5,
               'quant_tanq_uni_select_6': quant_tanq_uni_select_6,
               'quant_tanq_uni_select_7': quant_tanq_uni_select_7,
               'quant_tanq_uni_select_8': quant_tanq_uni_select_8,
               'quant_tanq_uni_select_9': quant_tanq_uni_select_9,
               'quant_tanq_uni_select_10': quant_tanq_uni_select_10,
               'cap_tot_arm_txt': cap_tot_arm_txt,
               'houve_sinistro': houve_sinistro,
               'prej_estim': prej_estim,
               'sinistro_data': sinistro_data,
               'ocorrencia_text': ocorrencia_text,
               'show_empty_data': False,
               'disabled_fields': disabled_fields,
               'just_viewing_form': just_viewing_form,
               'fotos': fotos,
               'laudo_object': laudo,
               'status': status,
               'percentual_req_tecnicos': float(int(percentual_req_tecnicos * 1000)) / 10}

    return context


def visualizar_editar_laudo(request, laudo_id):
    if request.user.is_authenticated():
        permissoes = PermissoesUsuario.objects.get(usuario=request.user)
        context = load_laudo_data(laudo_id, '', False)
        context['first_name'] = request.user.first_name
        context['last_name'] = request.user.last_name
        context['permissoes'] = permissoes
        return render(request, 'formulario_vistoria/add.html', context)
    else:
        return redirect('/login/')


def visualizar_laudo(request, laudo_id):
    if request.user.is_authenticated():
        permissoes = PermissoesUsuario.objects.get(usuario=request.user)
        context = load_laudo_data(laudo_id, 'disabled', True)
        context['first_name'] = request.user.first_name
        context['last_name'] = request.user.last_name
        context['permissoes'] = permissoes
        return render(request, 'formulario_vistoria/add.html', context)
    else:
        return redirect('/login/')


def preenchimento_formulario_vistoria(request, laudo_id):
    if request.user.is_authenticated():
        permissoes = PermissoesUsuario.objects.get(usuario=request.user)
        postos = Posto.objects.order_by('nome')
        laudo_obj = Laudo.objects.get(pk=laudo_id)
        selected_posto = laudo_obj.posto
        context = {'postos': postos, 'first_name': request.user.first_name, 'last_name': request.user.last_name, 'just_viewing_form': False, 'numero_proposta': laudo_obj.numero_proposta, 'selected_posto': selected_posto, 'laudo_object': laudo_obj, 'permissoes': permissoes}
        return render(request, 'formulario_vistoria/add.html', context)
    else:
        return redirect('/login/')


def carregar_laudos(post_data, permissoes, user):
    data_search = post_data.get('data_search', '')
    order_by = '-data_criacao'
    order_by_posto = ''
    if post_data.get('ordenar_por') == '0':
        order_by = '-numero_proposta'
    else:
        if post_data.get('ordenar_por') == '1':
            order_by = 'numero_proposta'
        else:
            if post_data.get('ordenar_por') == '2':
                order_by_posto = '-nome'
            else:
                if post_data.get('ordenar_por') == '3':
                    order_by_posto = 'nome'
                else:
                    if post_data.get('ordenar_por') == '4':
                        order_by = '-data_criacao'
                    else:
                        if post_data.get('ordenar_por') == '5':
                            order_by = 'data_criacao'
                        else:
                            if post_data.get('ordenar_por') == '6':
                                order_by = '-data_permissao'
                            else:
                                if post_data.get('ordenar_por') == '7':
                                    order_by = 'data_permissao'
                                else:
                                    if post_data.get('ordenar_por') == '8':
                                        order_by = '-status'
                                    else:
                                        if post_data.get('ordenar_por') == '9':
                                            order_by = 'status'
    if data_search == '':
        if order_by_posto == '':
            if permissoes.permissoes_clientes is True:
                laudos = Laudo.objects.filter(usuario=user).order_by(order_by)
            else:
                laudos = Laudo.objects.order_by(order_by)
        else:
            postos = Posto.objects.order_by(order_by_posto)
            laudos = []
            for posto in postos:
                if permissoes.permissoes_clientes is True:
                    laudos_query = Laudo.objects.filter(posto=posto).filter(usuario=user).order_by('-data_criacao')
                else:
                    laudos_query = Laudo.objects.filter(posto=posto).order_by('-data_criacao')
                for laudo in laudos_query:
                    laudos.append(laudo)
    else:
        postos = Posto.objects.filter(nome__icontains=data_search)
        if len(postos) != 0:
            laudos = []
            postos.order_by('nome')
            for posto in postos:
                if permissoes.permissoes_clientes is True:
                    laudos_query = Laudo.objects.filter(posto=posto).filter(usuario=user).order_by('-data_criacao')
                else:
                    laudos_query = Laudo.objects.filter(posto=posto).order_by('-data_criacao')
                for laudo in laudos_query:
                    laudos.append(laudo)
        else:
            if permissoes.permissoes_clientes is True:
                laudos = Laudo.objects.filter(numero_proposta=data_search).filter(usuario=user).order_by('-data_criacao')
            else:
                laudos = Laudo.objects.filter(numero_proposta=data_search).order_by('-data_criacao')
    laudos_novos = []
    laudos_antigos = []
    for i, laudo in enumerate(laudos):
        if laudo.status == 3:
            laudos_novos.append(laudo)
        else:
            laudos_antigos.append(laudo)
    return laudos_novos + laudos_antigos


def carregar_lista_laudos(request, pagina):
    if request.user.is_authenticated():
        permissoes = PermissoesUsuario.objects.get(usuario=request.user)
        post_data = request.POST
        if pagina != '' and pagina is not None:
            pagina = int(pagina)
        else:
            pagina = 1
        laudos = carregar_laudos(post_data, permissoes, request.user)
        pagina_anterior = pagina - 1 if pagina - 1 > 0 else -1
        pagina_posterior = pagina + 1 if pagina * LAUDOS_LIST_PAGE_SIZE <= len(laudos) else -1
        ordenacao = post_data.get('ordenar_por')
        ordenacao_0 = 'selected' if ordenacao == '0' else ''
        ordenacao_1 = 'selected' if ordenacao == '1' else ''
        ordenacao_2 = 'selected' if ordenacao == '2' else ''
        ordenacao_3 = 'selected' if ordenacao == '3' else ''
        ordenacao_4 = 'selected' if ordenacao == '4' else ''
        ordenacao_5 = 'selected' if ordenacao == '5' else ''
        ordenacao_6 = 'selected' if ordenacao == '6' else ''
        ordenacao_7 = 'selected' if ordenacao == '7' else ''
        ordenacao_8 = 'selected' if ordenacao == '8' else ''
        ordenacao_9 = 'selected' if ordenacao == '9' else ''
        context = {'laudos': laudos[(pagina - 1) * LAUDOS_LIST_PAGE_SIZE:pagina * LAUDOS_LIST_PAGE_SIZE], 'first_name': request.user.first_name, 'last_name': request.user.last_name, 'pesquisa_laudo': post_data.get('data_search', ''), 'ordenacao_0': ordenacao_0, 'ordenacao_1': ordenacao_1, 'ordenacao_2': ordenacao_2, 'ordenacao_3': ordenacao_3, 'ordenacao_4': ordenacao_4, 'ordenacao_5': ordenacao_5, 'ordenacao_6': ordenacao_6, 'ordenacao_7': ordenacao_7, 'ordenacao_8': ordenacao_8, 'ordenacao_9': ordenacao_9, 'pagina_corrente': pagina, 'pagina_anterior': pagina_anterior, 'pagina_posterior': pagina_posterior, 'permissoes': permissoes}
        return render(request, 'formulario_vistoria/index.html', context)
    else:
        return redirect('/login/')


def carregar_lista_laudos_confirmacao_registro(request, pagina):
    if request.user.is_authenticated():
        permissoes = PermissoesUsuario.objects.get(usuario=request.user)
        post_data = request.POST
        if pagina != '' and pagina is not None:
            pagina = int(pagina)
        else:
            pagina = 1
        laudos = carregar_laudos(post_data, permissoes, request.user)
        pagina_anterior = pagina - 1 if pagina - 1 >= 0 else -1
        pagina_posterior = pagina + 1 if pagina * LAUDOS_LIST_PAGE_SIZE <= len(laudos) else -1
        ordenacao = post_data.get('ordenar_por')
        ordenacao_0 = 'selected' if ordenacao == '0' else ''
        ordenacao_1 = 'selected' if ordenacao == '1' else ''
        ordenacao_2 = 'selected' if ordenacao == '2' else ''
        ordenacao_3 = 'selected' if ordenacao == '3' else ''
        ordenacao_4 = 'selected' if ordenacao == '4' else ''
        ordenacao_5 = 'selected' if ordenacao == '5' else ''
        ordenacao_6 = 'selected' if ordenacao == '6' else ''
        ordenacao_7 = 'selected' if ordenacao == '7' else ''
        ordenacao_8 = 'selected' if ordenacao == '8' else ''
        ordenacao_9 = 'selected' if ordenacao == '9' else ''
        context = {'laudos': laudos, 'first_name': request.user.first_name, 'last_name': request.user.last_name, 'show_empty_data': True, 'pesquisa_laudo': post_data.get('data_search', ''), 'ordenacao_0': ordenacao_0, 'ordenacao_1': ordenacao_1, 'ordenacao_2': ordenacao_2, 'ordenacao_3': ordenacao_3, 'ordenacao_4': ordenacao_4, 'ordenacao_5': ordenacao_5, 'ordenacao_6': ordenacao_6, 'ordenacao_7': ordenacao_7, 'ordenacao_8': ordenacao_8, 'ordenacao_9': ordenacao_9, 'pagina_corrente': pagina, 'pagina_anterior': pagina_anterior, 'pagina_posterior': pagina_posterior, 'permissoes': permissoes}
        return render(request, 'formulario_vistoria/index.html', context)
    else:
        return redirect('/login/')


estado_conservacao_dict = {'Indisponível': -1, 'Precário': 0, 'Regular': 1, 'Bom': 2}
licenca_ambiental_dict = {'Inexistente/Vencido': -1, 'LP': 0, 'LI': 1, 'LO': 2}


@csrf_exempt
def foto_upload(request):
    user_id = request.user.id
    username = request.user.username
    user_first_name = request.user.first_name
    user_last_name = request.user.last_name
    directory = MEDIA_ROOT + '/fotos/' + user_first_name + '_' + user_last_name + '_' + str(user_id)
    os.makedirs(directory, exist_ok=True)
    timestamp = datetime.now()
    filename = 'NOVO-' + str(user_id) + username + str(timestamp.year) + str(timestamp.month) + str(timestamp.day) + str(timestamp.hour) + str(timestamp.minute) + str(timestamp.second) + str(timestamp.microsecond) + '.' + request.FILES['fotos-upload'].name.split('.')[1]
    with open(directory + '/' + filename, 'wb+') as destination:
        for chunk in request.FILES['fotos-upload'].chunks():
            destination.write(chunk)
    return render(request, 'formulario_vistoria/empty_json.json')


def linkar_fotos_laudo(laudo_id, request):
    user_id = request.user.id
    user_first_name = request.user.first_name
    user_last_name = request.user.last_name
    directory = MEDIA_ROOT + '/fotos/' + user_first_name + '_' + user_last_name + '_' + str(user_id)
    if not os.path.exists(directory):
        os.makedirs(directory)
    files = os.listdir(directory)
    if len(files) != 0:
        for file in files:
            if file.startswith('NOVO-'):
                os.rename(directory + '/' + file, directory + '/' + file[5:])
                file = file[5:]
                foto = Foto(endereco=directory + '/' + file, laudo=Laudo.objects.get(id=laudo_id))
                foto.save()


def foto_delete(request):
    return render(request, 'formulario_vistoria/empty_json.json')


def validate_form_fill(radio_reg_anp, reg_anp_num,
                       registro_anp_data_expedicao, registro_anp_validade,
                       radio_alv_func, alv_func_num, alv_func_data_expedicao,
                       alv_func_validade, radio_lic_amb, lic_amb_num,
                       lic_amb_data_expedicao, lic_amb_validade,
                       radio_atest_reg, atest_reg_num,
                       atest_reg_data_expedicao, atest_reg_validade,
                       cap_tot_arm_txt, houve_sinistro, prej_estim,
                       sinistro_data, ocorrencia_text):
    invalid_fields = []

    if radio_reg_anp is not None:
        if reg_anp_num == '' or reg_anp_num is None:
            invalid_fields.append('reg_anp_num')
        if registro_anp_data_expedicao == '' or registro_anp_data_expedicao is None:
            invalid_fields.append('registro_anp_data_expedicao')
        if registro_anp_validade == '' or registro_anp_validade is None:
            invalid_fields.append('registro_anp_validade')

    if radio_alv_func is not None:
        if alv_func_num == '' or alv_func_num is None:
            invalid_fields.append('alv_func_num')
        if alv_func_data_expedicao == '' or alv_func_data_expedicao is None:
            invalid_fields.append('alv_func_data_expedicao')
        if alv_func_validade == '' or alv_func_validade is None:
            invalid_fields.append('alv_func_validade')

    if radio_lic_amb != -1 and radio_lic_amb is not None:
        if lic_amb_num == '' or lic_amb_num is None:
            invalid_fields.append('lic_amb_num')
        if lic_amb_data_expedicao == '' or lic_amb_data_expedicao is None:
            invalid_fields.append('lic_amb_data_expedicao')
        if lic_amb_validade == '' or lic_amb_validade is None:
            invalid_fields.append('lic_amb_validade')

    if radio_atest_reg is not False:
        if atest_reg_num == '' or atest_reg_num is None:
            invalid_fields.append('atest_reg_num')
        if atest_reg_data_expedicao == '' or atest_reg_data_expedicao is None:
            invalid_fields.append('atest_reg_data_expedicao')
        if atest_reg_validade == '' or atest_reg_validade is None:
            invalid_fields.append('atest_reg_validade')

    if cap_tot_arm_txt == '' or cap_tot_arm_txt is None:
        invalid_fields.append('cap_tot_arm_txt')

    if houve_sinistro is not False:
        if prej_estim == '' or prej_estim is None:
            invalid_fields.append('prej_estim')
        if sinistro_data == '' or sinistro_data is None:
            invalid_fields.append('sinistro_data')
        if ocorrencia_text == '' or ocorrencia_text is None:
            invalid_fields.append('ocorrencia_text')

    return {'is_valid_data': (len(invalid_fields) == 0),
            'invalid_fields': invalid_fields}


def save_form_vistoria(request, laudo):

    post_data = request.POST

    permissoes = PermissoesUsuario.objects.get(usuario=request.user)

    radio_reg_anp = None
    if post_data.get('radio_reg_anp', None) == 'Definitivo':
        radio_reg_anp = True
    else:
        if post_data.get('radio_reg_anp', None) == 'Provisório':
            radio_reg_anp = False

    reg_anp_num = post_data.get('reg_anp_num', None)
    registro_anp_data_expedicao = post_data.get('registro_anp_data_expedicao', None)
    if registro_anp_data_expedicao == '':
        registro_anp_data_expedicao = None

    registro_anp_validade = post_data.get('registro_anp_validade', None)
    if registro_anp_validade == '':
        registro_anp_validade = None

    radio_alv_func = None
    if post_data.get('radio_alv_func', None) == 'Definitivo':
        radio_alv_func = True
    else:
        if post_data.get('radio_alv_func', None) == 'Provisório':
            radio_alv_func = False

    alv_func_num = post_data.get('alv_func_num', None)
    alv_func_data_expedicao = post_data.get('alv_func_data_expedicao', None)
    if alv_func_data_expedicao == '':
        alv_func_data_expedicao = None

    alv_func_validade = post_data.get('alv_func_validade', None)
    if alv_func_validade == '':
        alv_func_validade = None

    radio_lic_amb = post_data.get('radio_lic_amb', None)
    if radio_lic_amb is not None:
        radio_lic_amb = licenca_ambiental_dict[radio_lic_amb]

    lic_amb_num = post_data.get('lic_amb_num', None)
    lic_amb_data_expedicao = post_data.get('lic_amb_data_expedicao', None)
    if lic_amb_data_expedicao == '':
        lic_amb_data_expedicao = None

    lic_amb_validade = post_data.get('lic_amb_validade', None)
    if lic_amb_validade == '':
        lic_amb_validade = None

    radio_atest_reg = False
    if post_data.get('radio_atest_reg', None) == 'Sim':
        radio_atest_reg = True

    atest_reg_num = post_data.get('atest_reg_num', None)
    atest_reg_data_expedicao = post_data.get('atest_reg_data_expedicao', None)
    if atest_reg_data_expedicao == '':
        atest_reg_data_expedicao = None

    atest_reg_validade = post_data.get('atest_reg_validade', None)
    if atest_reg_validade == '':
        atest_reg_validade = None

    observacao = post_data.get('observacao', None)

    serv_venda_comb = False if post_data.get('serv_venda_comb', None) is None else True
    serv_troca_oleo = False if post_data.get('serv_troca_oleo', None) is None else True
    serv_lav_veiculos = False if post_data.get('serv_lav_veiculos', None) is None else True
    serv_ofic_mec = False if post_data.get('serv_ofic_mec', None) is None else True
    serv_lanc_conven = False if post_data.get('serv_lanc_conven', None) is None else True
    serv_gas_cozinha = False if post_data.get('serv_gas_cozinha', None) is None else True

    outros_servicos = post_data.get('outros_servicos', None)

    radio_val_ret_vap = post_data.get('radio_val_ret_vap', None)
    if radio_val_ret_vap is not None:
        radio_val_ret_vap = estado_conservacao_dict[radio_val_ret_vap]
    valv_ret_vap = False if radio_val_ret_vap == -1 else True

    tanq_sub_par_dup_jaq = False if post_data.get('tanq_sub_par_dup_jaq', None) is None else True
    tanq_sub_par_dup_jaq_data_inst = post_data.get('tanq_sub_par_dup_jaq_data_inst', None)
    if tanq_sub_par_dup_jaq_data_inst == '':
        tanq_sub_par_dup_jaq_data_inst = None

    radio_poco_mon = post_data.get('radio_poco_mon', None)
    if radio_poco_mon is not None:
        radio_poco_mon = estado_conservacao_dict[radio_poco_mon]
    poco_mon = False if radio_poco_mon == -1 else True

    radio_can_ilha_bom = post_data.get('radio_can_ilha_bom', None)
    if radio_can_ilha_bom is not None:
        radio_can_ilha_bom = estado_conservacao_dict[radio_can_ilha_bom]
    can_ilha_bom = False if radio_can_ilha_bom == -1 else True

    radio_can_per = post_data.get('radio_can_per', None)
    if radio_can_per is not None:
        radio_can_per = estado_conservacao_dict[radio_can_per]
    can_per = False if radio_can_per == -1 else True

    radio_piso_alisado_bombas = post_data.get('radio_piso_alisado_bombas', None)
    if radio_piso_alisado_bombas is not None:
        radio_piso_alisado_bombas = estado_conservacao_dict[radio_piso_alisado_bombas]
    piso_alisado_bombas = False if radio_piso_alisado_bombas == -1 else True

    radio_sist_det_vaz = post_data.get('radio_sist_det_vaz', None)
    if radio_sist_det_vaz is not None:
        radio_sist_det_vaz = estado_conservacao_dict[radio_sist_det_vaz]
    sist_det_vaz = False if radio_sist_det_vaz == -1 else True

    radio_can_int_sao = post_data.get('radio_can_int_sao', None)
    if radio_can_int_sao is not None:
        radio_can_int_sao = estado_conservacao_dict[radio_can_int_sao]
    can_int_sao = False if radio_can_int_sao == -1 else True

    radio_lav_vei_piso_can_sao = post_data.get('radio_lav_vei_piso_can_sao', None)
    if radio_lav_vei_piso_can_sao is not None:
        radio_lav_vei_piso_can_sao = estado_conservacao_dict[radio_lav_vei_piso_can_sao]
    lav_vei_piso_can_sao = False if radio_lav_vei_piso_can_sao == -1 is None else True

    radio_area_oleo_piso = post_data.get('radio_area_oleo_piso', None)
    if radio_area_oleo_piso is not None:
        radio_area_oleo_piso = estado_conservacao_dict[radio_area_oleo_piso]
    area_oleo_piso = False if radio_area_oleo_piso == -1 else True

    radio_area_res_piso = post_data.get('radio_area_res_piso', None)
    if radio_area_res_piso is not None:
        radio_area_res_piso = estado_conservacao_dict[radio_area_res_piso]
    area_res_piso = False if radio_area_res_piso == -1 else True

    at_red_pub_san = False if post_data.get('at_red_pub_san', None) is None else True

    quant_tanq_uni_select = post_data.get('quant_tanq_uni_select', None)
    cap_tot_arm_txt = post_data.get('cap_tot_arm_txt', None)
    if cap_tot_arm_txt == '':
        cap_tot_arm_txt = 0

    houve_sinistro = False if post_data.get('houve_sinistro', None) is None else True

    prej_estim = post_data.get('prej_estim', None)
    if prej_estim == '':
        prej_estim = 0.0

    sinistro_data = post_data.get('sinistro_data', None)
    if sinistro_data == '':
        sinistro_data = None

    ocorrencia_text = post_data.get('ocorrencia_text', None)

    validation_data = validate_form_fill(radio_reg_anp,
                                         reg_anp_num,
                                         registro_anp_data_expedicao,
                                         registro_anp_validade,
                                         radio_alv_func, alv_func_num,
                                         alv_func_data_expedicao,
                                         alv_func_validade, radio_lic_amb,
                                         lic_amb_num, lic_amb_data_expedicao,
                                         lic_amb_validade, radio_atest_reg,
                                         atest_reg_num,
                                         atest_reg_data_expedicao,
                                         atest_reg_validade, cap_tot_arm_txt,
                                         houve_sinistro, prej_estim,
                                         sinistro_data, ocorrencia_text)
    is_valid_data = validation_data['is_valid_data']
    invalid_fields = validation_data['invalid_fields']
    postos = Posto.objects.order_by('nome')
    laudo_obj = Laudo.objects.get(pk=laudo)
    selected_posto = laudo_obj.posto
    numero_proposta = laudo_obj.numero_proposta
    context = {'first_name': request.user.first_name,
               'last_name': request.user.last_name,
               'show_empty_data': True}

    if is_valid_data:
        laudo_obj.status = 0
        if radio_reg_anp is not None:
            laudo_obj.registro_anp_definitivo = radio_reg_anp
        if reg_anp_num is not None:
            laudo_obj.registro_anp_numero = reg_anp_num
        if registro_anp_data_expedicao is not None:
            laudo_obj.registro_anp_data_expedicao = registro_anp_data_expedicao
        if registro_anp_validade is not None:
            laudo_obj.registro_anp_data_validade = registro_anp_validade
        if radio_alv_func is not None:
            laudo_obj.alvara_funcionamento_definitivo = radio_alv_func
        if alv_func_num is not None:
            laudo_obj.alvara_funcionamento_numero = alv_func_num
        if alv_func_data_expedicao is not None:
            laudo_obj.alvara_funcionamento_data_expedicao = alv_func_data_expedicao
        if alv_func_validade is not None:
            laudo_obj.alvara_funcionamento_data_validade = alv_func_validade
        if radio_lic_amb is not None:
            laudo_obj.licenca_ambiental = radio_lic_amb
        if lic_amb_num is not None:
            laudo_obj.licenca_ambiental_numero = lic_amb_num
        if lic_amb_data_expedicao is not None:
            laudo_obj.licenca_ambiental_data_expedicao = lic_amb_data_expedicao
        if lic_amb_validade is not None:
            laudo_obj.licenca_ambiental_data_validade = lic_amb_validade
        if radio_atest_reg is not None:
            laudo_obj.atestado_regularidade_ar_sim = radio_atest_reg
        if atest_reg_num is not None:
            laudo_obj.atestado_regularidade_ar_numero = atest_reg_num
        if atest_reg_data_expedicao is not None:
            laudo_obj.atestado_regularidade_ar_data_expedicao = atest_reg_data_expedicao
        if atest_reg_validade is not None:
            laudo_obj.atestado_regularidade_ar_data_validade = atest_reg_validade
        if observacao is not None:
            laudo_obj.observacao = observacao
        if serv_venda_comb is not None:
            laudo_obj.venda_combustiveis_disponivel = serv_venda_comb
        if serv_lav_veiculos is not None:
            laudo_obj.lavagem_viculos_disponivel = serv_lav_veiculos
        if serv_lanc_conven is not None:
            laudo_obj.restaurante_lanchonete_conveniencia_disponivel = serv_lanc_conven
        if serv_troca_oleo is not None:
            laudo_obj.troca_oleo_disponivel = serv_troca_oleo
        if serv_ofic_mec is not None:
            laudo_obj.oficina_mecanica_disponivel = serv_ofic_mec
        if serv_gas_cozinha is not None:
            laudo_obj.venda_gas_cozinha = serv_gas_cozinha
        if outros_servicos is not None:
            laudo_obj.outros_servicos_disponibilidade = outros_servicos
        if valv_ret_vap is not None:
            laudo_obj.valvula_retentora_vapor_disponibilidade = valv_ret_vap
        if radio_val_ret_vap is not None:
            laudo_obj.valvula_retentora_vapor_estado_conservacao = radio_val_ret_vap
        if tanq_sub_par_dup_jaq is not None:
            laudo_obj.tanque_sub_parede_dupla_jaquetado = tanq_sub_par_dup_jaq
        if tanq_sub_par_dup_jaq_data_inst is not None:
            laudo_obj.tanque_sub_parede_data_instalacao = tanq_sub_par_dup_jaq_data_inst
        if poco_mon is not None:
            laudo_obj.poco_monitoramento_disponibilidade = poco_mon
        if radio_poco_mon is not None:
            laudo_obj.poco_monitoramento_estado_conservacao = radio_poco_mon
        if can_ilha_bom is not None:
            laudo_obj.caneletas_ilhas_bombas_disponibilidade = can_ilha_bom
        if radio_can_ilha_bom is not None:
            laudo_obj.caneletas_ilhas_bombas_estado_conservacao = radio_can_ilha_bom
        if can_per is not None:
            laudo_obj.caneletas_perimetro_disponibilidade = can_per
        if radio_can_per is not None:
            laudo_obj.caneletas_perimetro_estado_conservacao = radio_can_per
        if piso_alisado_bombas is not None:
            laudo_obj.piso_concreto_alisado_disponibilidade = piso_alisado_bombas
        if radio_piso_alisado_bombas is not None:
            laudo_obj.piso_concreto_alisado_estado_conservacao = radio_piso_alisado_bombas
        if can_int_sao is not None:
            laudo_obj.caneletas_interligadas_sao_disponibilidade = can_int_sao
        if radio_can_int_sao is not None:
            laudo_obj.caneletas_interligadas_sao_estado_conservacao = radio_can_int_sao
        if sist_det_vaz is not None:
            laudo_obj.sistema_deteccao_vazamento_disponibilidade = sist_det_vaz
        if radio_sist_det_vaz is not None:
            laudo_obj.sistema_deteccao_vazamento_estado_conservacao = radio_sist_det_vaz
        if lav_vei_piso_can_sao is not None:
            laudo_obj.area_lavagem_piso_can_sao_disponibilidade = lav_vei_piso_can_sao
        if radio_lav_vei_piso_can_sao is not None:
            laudo_obj.area_lavagem_piso_can_sao_estado_conservacao = radio_lav_vei_piso_can_sao
        if area_oleo_piso is not None:
            laudo_obj.area_troca_oleo_piso_can_sao_disponibilidade = area_oleo_piso
        if radio_area_oleo_piso is not None:
            laudo_obj.area_troca_oleo_piso_can_sao_estado_conservacao = radio_area_oleo_piso
        if area_res_piso is not None:
            laudo_obj.area_armazenamento_residuos_coberta_piso_disponibilidade = area_res_piso
        if radio_area_res_piso is not None:
            laudo_obj.area_armazenamento_residuos_coberta_piso_estado_conservacao = radio_area_res_piso
        if at_red_pub_san is not None:
            laudo_obj.atendido_rede_publica_saneamento = at_red_pub_san
        if quant_tanq_uni_select is not None:
            laudo_obj.quantidade_tanques = quant_tanq_uni_select
        if cap_tot_arm_txt is not None:
            laudo_obj.capacidade_armazenamento = cap_tot_arm_txt
        if houve_sinistro is not None:
            laudo_obj.houve_sinistro_ultimos_anos = houve_sinistro
        if prej_estim is not None:
            laudo_obj.prejuizo_estimativa = prej_estim
        if sinistro_data is not None:
            laudo_obj.data_sinistro = sinistro_data
        if ocorrencia_text is not None:
            laudo_obj.ocorrencia = ocorrencia_text

        laudo_obj.save()
        linkar_fotos_laudo(laudo_obj.id, request)

        return redirect('/formulario_vistoria/index/registration_confirm/1', context)
    else:
        context['show_empty_data'] = False
        context['numero_proposta'] = numero_proposta if numero_proposta is not None else ''
        context['radio_reg_anp'] = radio_reg_anp
        context['reg_anp_num'] = reg_anp_num if reg_anp_num is not None else ''
        context['registro_anp_data_expedicao'] = registro_anp_data_expedicao
        context['registro_anp_validade'] = registro_anp_validade
        context['radio_alv_func'] = radio_alv_func
        context['alv_func_num'] = alv_func_num if alv_func_num is not None else ''
        context['alv_func_data_expedicao'] = alv_func_data_expedicao
        context['alv_func_validade'] = alv_func_validade
        context['radio_lic_amb'] = radio_lic_amb
        context['lic_amb_num'] = lic_amb_num if lic_amb_num is not None else ''
        context['lic_amb_data_expedicao'] = lic_amb_data_expedicao
        context['lic_amb_validade'] = lic_amb_validade
        context['radio_atest_reg'] = radio_atest_reg
        context['atest_reg_num'] = atest_reg_num if atest_reg_num is not None else ''
        context['atest_reg_data_expedicao'] = atest_reg_data_expedicao
        context['atest_reg_validade'] = atest_reg_validade
        context['observacao'] = observacao if observacao is not None else ''
        context['serv_venda_comb'] = 'checked' if serv_venda_comb is True else ''
        context['serv_lav_veiculos'] = 'checked' if serv_lav_veiculos is True else ''
        context['serv_lanc_conven'] = 'checked' if serv_lanc_conven is True else ''
        context['serv_troca_oleo'] = 'checked' if serv_troca_oleo is True else ''
        context['serv_ofic_mec'] = 'checked' if serv_ofic_mec is True else ''
        context['serv_gas_cozinha'] = 'checked' if serv_gas_cozinha is True else ''
        context['outros_servicos'] = outros_servicos
        context['valv_ret_vap'] = 'checked' if valv_ret_vap is True else ''
        context['radio_val_ret_vap_0'] = 'checked' if radio_val_ret_vap == -1 else ''
        context['radio_val_ret_vap_1'] = 'checked' if radio_val_ret_vap == 2 else ''
        context['radio_val_ret_vap_2'] = 'checked' if radio_val_ret_vap == 1 else ''
        context['radio_val_ret_vap_3'] = 'checked' if radio_val_ret_vap == 0 else ''
        context['tanq_sub_par_dup_jaq'] = 'checked' if tanq_sub_par_dup_jaq is True else ''
        context['tanq_sub_par_dup_jaq_data_inst'] = tanq_sub_par_dup_jaq_data_inst
        context['poco_mon'] = 'checked' if poco_mon is True else ''
        context['radio_poco_mon_0'] = 'checked' if radio_poco_mon == -1 else ''
        context['radio_poco_mon_1'] = 'checked' if radio_poco_mon == 2 else ''
        context['radio_poco_mon_2'] = 'checked' if radio_poco_mon == 1 else ''
        context['radio_poco_mon_3'] = 'checked' if radio_poco_mon == 0 else ''
        context['can_ilha_bom'] = 'checked' if can_ilha_bom is True else ''
        context['radio_can_ilha_bom_0'] = 'checked' if radio_can_ilha_bom == -1 else ''
        context['radio_can_ilha_bom_1'] = 'checked' if radio_can_ilha_bom == 2 else ''
        context['radio_can_ilha_bom_2'] = 'checked' if radio_can_ilha_bom == 1 else ''
        context['radio_can_ilha_bom_3'] = 'checked' if radio_can_ilha_bom == 0 else ''
        context['can_per'] = 'checked' if can_per is True else ''
        context['radio_can_per_0'] = 'checked' if radio_can_per == -1 else ''
        context['radio_can_per_1'] = 'checked' if radio_can_per == 2 else ''
        context['radio_can_per_2'] = 'checked' if radio_can_per == 1 else ''
        context['radio_can_per_3'] = 'checked' if radio_can_per == 0 else ''
        context['piso_alisado_bombas'] = 'checked' if piso_alisado_bombas is True else ''
        context['radio_piso_alisado_bombas_0'] = 'checked' if radio_piso_alisado_bombas == -1 else ''
        context['radio_piso_alisado_bombas_1'] = 'checked' if radio_piso_alisado_bombas == 2 else ''
        context['radio_piso_alisado_bombas_2'] = 'checked' if radio_piso_alisado_bombas == 1 else ''
        context['radio_piso_alisado_bombas_3'] = 'checked' if radio_piso_alisado_bombas == 0 else ''
        context['can_int_sao'] = 'checked' if can_int_sao is True else ''
        context['radio_can_int_sao_0'] = 'checked' if radio_can_int_sao == -1 else ''
        context['radio_can_int_sao_1'] = 'checked' if radio_can_int_sao == 2 else ''
        context['radio_can_int_sao_2'] = 'checked' if radio_can_int_sao == 1 else ''
        context['radio_can_int_sao_3'] = 'checked' if radio_can_int_sao == 0 else ''
        context['sist_det_vaz'] = 'checked' if sist_det_vaz is True else ''
        context['radio_sist_det_vaz_0'] = 'checked' if radio_sist_det_vaz == -1 else ''
        context['radio_sist_det_vaz_1'] = 'checked' if radio_sist_det_vaz == 2 else ''
        context['radio_sist_det_vaz_2'] = 'checked' if radio_sist_det_vaz == 1 else ''
        context['radio_sist_det_vaz_3'] = 'checked' if radio_sist_det_vaz == 0 else ''
        context['lav_vei_piso_can_sao'] = 'checked' if lav_vei_piso_can_sao is True else ''
        context['radio_lav_vei_piso_can_sao_0'] = 'checked' if radio_lav_vei_piso_can_sao == -1 else ''
        context['radio_lav_vei_piso_can_sao_1'] = 'checked' if radio_lav_vei_piso_can_sao == 2 else ''
        context['radio_lav_vei_piso_can_sao_2'] = 'checked' if radio_lav_vei_piso_can_sao == 1 else ''
        context['radio_lav_vei_piso_can_sao_3'] = 'checked' if radio_lav_vei_piso_can_sao == 0 else ''
        context['area_oleo_piso'] = 'checked' if area_oleo_piso is True else ''
        context['radio_area_oleo_piso_0'] = 'checked' if radio_area_oleo_piso == -1 else ''
        context['radio_area_oleo_piso_1'] = 'checked' if radio_area_oleo_piso == 2 else ''
        context['radio_area_oleo_piso_2'] = 'checked' if radio_area_oleo_piso == 1 else ''
        context['radio_area_oleo_piso_3'] = 'checked' if radio_area_oleo_piso == 0 else ''
        context['area_res_piso'] = 'checked' if area_res_piso is True else ''
        context['radio_area_res_piso_0'] = 'checked' if radio_area_res_piso == -1 else ''
        context['radio_area_res_piso_1'] = 'checked' if radio_area_res_piso == 2 else ''
        context['radio_area_res_piso_2'] = 'checked' if radio_area_res_piso == 1 else ''
        context['radio_area_res_piso_3'] = 'checked' if radio_area_res_piso == 0 else ''
        context['at_red_pub_san'] = 'checked' if at_red_pub_san is True else ''
        context['quant_tanq_uni_select_1'] = 'selected' if quant_tanq_uni_select == '1' else ''
        context['quant_tanq_uni_select_2'] = 'selected' if quant_tanq_uni_select == '2' else ''
        context['quant_tanq_uni_select_3'] = 'selected' if quant_tanq_uni_select == '3' else ''
        context['quant_tanq_uni_select_4'] = 'selected' if quant_tanq_uni_select == '4' else ''
        context['quant_tanq_uni_select_5'] = 'selected' if quant_tanq_uni_select == '5' else ''
        context['quant_tanq_uni_select_6'] = 'selected' if quant_tanq_uni_select == '6' else ''
        context['quant_tanq_uni_select_7'] = 'selected' if quant_tanq_uni_select == '7' else ''
        context['quant_tanq_uni_select_8'] = 'selected' if quant_tanq_uni_select == '8' else ''
        context['quant_tanq_uni_select_9'] = 'selected' if quant_tanq_uni_select == '9' else ''
        context['quant_tanq_uni_select_10'] = 'selected' if quant_tanq_uni_select == '10' else ''
        context['cap_tot_arm_txt'] = cap_tot_arm_txt if cap_tot_arm_txt is not None else ''
        context['houve_sinistro'] = 'checked' if houve_sinistro is True else ''
        context['prej_estim'] = prej_estim if prej_estim is not None else ''
        context['sinistro_data'] = sinistro_data
        context['ocorrencia_text'] = ocorrencia_text if ocorrencia_text is not None else ''
        context['invalid_fields'] = invalid_fields
        context['first_name'] = request.user.first_name
        context['last_name'] = request.user.last_name
        context['selected_posto'] = selected_posto
        context['postos'] = postos
        context['disabled_fields'] = ''
        context['just_viewing_form'] = False
        context['invalid_form'] = True
        context['laudo_object'] = laudo_obj
        context['permissoes'] = permissoes
        return render(request, 'formulario_vistoria/add.html', context)


def fill_posto_db(request):

    f = open("PLANILHA POSTOS - BASE DE CADASTRO.csv", 'r')
    lines = f.readlines()

    Posto.objects.all().delete()

    for i, line in enumerate(lines[1:]):
        print(float(i) / len(lines[1:]))
        line = line.split('\n')[0]
        data = (line.split(';'))
        posto = Posto(nome=data[1], endereco=data[2], bairro=data[3], cnpj=data[4])
        posto.save()

    return render(request, 'formulario_vistoria/ok.html')
