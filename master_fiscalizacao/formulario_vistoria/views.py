from django.shortcuts import render
from django.contrib.auth.models import User
from .models import Posto, Laudo
from django.views.decorators.csrf import csrf_exempt
from master_fiscalizacao.settings import MEDIA_ROOT
from datetime import datetime
import os


def visualizar_laudo(request):
    return render(request, 'formulario_vistoria/view.html')


def preenchimento_formulario_vistoria(request):
    postos = Posto.objects.order_by('nome')
    context = {'postos': postos}
    return render(request, 'formulario_vistoria/add.html', context)


def carregar_lista_laudos(request):
    post_data = request.POST
    data_search = post_data.get('data_search', '')
    if data_search == '':
        laudos = Laudo.objects.order_by('-data_criacao')
    else:
        postos = Posto.objects.filter(nome__icontains=data_search)
        if len(postos) != 0:
            laudos = []
            for posto in postos:
                laudos_query = Laudo.objects.filter(posto=posto)
                for laudo in laudos_query:
                    laudos.append(laudo)
        else:
            laudos = Laudo.objects.filter(numero_proposta=data_search).order_by('-data_criacao')
    context = {'laudos': laudos}
    return render(request, 'formulario_vistoria/index.html', context)


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


def foto_delete(request):
    return render(request, 'formulario_vistoria/empty_json.json')


def save_form_vistoria(request):    
    post_data = request.POST

    posto_id = post_data.get('id_posto', None)
    posto = Posto.objects.get(id=posto_id)
    numero_proposta = post_data.get('input_num_proposta', None)

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

    serv_outros = post_data.get('serv_outros', None)
    outros_servicos = ''
    if serv_outros:
        outros_servicos = post_data.get('outros_servicos', None)

    valv_ret_vap = False if post_data.get('valv_ret_vap', None) is None else True
    radio_val_ret_vap = post_data.get('radio_val_ret_vap', None)
    if radio_val_ret_vap is not None:
        radio_val_ret_vap = estado_conservacao_dict[radio_val_ret_vap]

    tanq_sub_par_dup_jaq = False if post_data.get('tanq_sub_par_dup_jaq', None) is None else True
    tanq_sub_par_dup_jaq_data_inst = post_data.get('tanq_sub_par_dup_jaq_data_inst', None)
    if tanq_sub_par_dup_jaq_data_inst == '':
        tanq_sub_par_dup_jaq_data_inst = None

    poco_mon = False if post_data.get('poco_mon', None) is None else True
    radio_poco_mon = post_data.get('radio_poco_mon', None)
    if radio_poco_mon is not None:
        radio_poco_mon = estado_conservacao_dict[radio_poco_mon]

    can_ilha_bom = False if post_data.get('can_ilha_bom', None) is None else True
    radio_can_ilha_bom = post_data.get('radio_can_ilha_bom', None)
    if radio_can_ilha_bom is not None:
        radio_can_ilha_bom = estado_conservacao_dict[radio_can_ilha_bom]

    can_per = False if post_data.get('can_per', None) is None else True
    radio_can_per = post_data.get('radio_can_per', None)
    if radio_can_per is not None:
        radio_can_per = estado_conservacao_dict[radio_can_per]

    piso_alisado_bombas = False if post_data.get('piso_alisado_bombas', None) is None else True
    radio_piso_alisado_bombas = post_data.get('radio_piso_alisado_bombas', None)
    if radio_piso_alisado_bombas is not None:
        radio_piso_alisado_bombas = estado_conservacao_dict[radio_piso_alisado_bombas]

    sist_det_vaz = False if post_data.get('sist_det_vaz', None) is None else True
    radio_sist_det_vaz = post_data.get('radio_sist_det_vaz', None)
    if radio_sist_det_vaz is not None:
        radio_sist_det_vaz = estado_conservacao_dict[radio_sist_det_vaz]

    can_int_sao = False if post_data.get('can_int_sao', None) is None else True
    radio_can_int_sao = post_data.get('radio_can_int_sao', None)
    if radio_can_int_sao is not None:
        radio_can_int_sao = estado_conservacao_dict[radio_can_int_sao]

    lav_vei_piso_can_sao = False if post_data.get('lav_vei_piso_can_sao', None) is None else True
    radio_lav_vei_piso_can_sao = post_data.get('radio_lav_vei_piso_can_sao', None)
    if radio_lav_vei_piso_can_sao is not None:
        radio_lav_vei_piso_can_sao = estado_conservacao_dict[radio_lav_vei_piso_can_sao]

    area_oleo_piso = False if post_data.get('area_oleo_piso', None) is None else True
    radio_area_oleo_piso = post_data.get('radio_area_oleo_piso', None)
    if radio_area_oleo_piso is not None:
        radio_area_oleo_piso = estado_conservacao_dict[radio_area_oleo_piso]

    area_res_piso = False if post_data.get('area_res_piso', None) is None else True
    radio_area_res_piso = post_data.get('radio_area_res_piso', None)
    if radio_area_res_piso is not None:
        radio_area_res_piso = estado_conservacao_dict[radio_area_res_piso]

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

    data_criacao = datetime.now()

    laudo = Laudo(satus=0, data_criacao=data_criacao, usuario=User.objects.get(id=request.user.id), posto=posto, numero_proposta=numero_proposta, registro_anp_definitivo=radio_reg_anp, registro_anp_numero=reg_anp_num, registro_anp_data_expedicao=registro_anp_data_expedicao, registro_anp_data_validade=registro_anp_validade, alvara_funcionamento_definitivo=radio_alv_func, alvara_funcionamento_numero=alv_func_num, alvara_funcionamento_data_expedicao=alv_func_data_expedicao, alvara_funcionamento_data_validade=alv_func_validade, licenca_ambiental=radio_lic_amb, licenca_ambiental_numero=lic_amb_num, licenca_ambiental_data_expedicao=lic_amb_data_expedicao, licenca_ambiental_data_validade=lic_amb_validade, atestado_regularidade_ar_sim=radio_atest_reg, atestado_regularidade_ar_numero=atest_reg_num, atestado_regularidade_ar_data_expedicao=atest_reg_data_expedicao, atestado_regularidade_ar_data_validade=atest_reg_validade, observacao=observacao, venda_combustiveis_disponivel=serv_venda_comb, lavagem_viculos_disponivel=serv_lav_veiculos, restaurante_lanchonete_conveniencia_disponivel=serv_lanc_conven, troca_oleo_disponivel=serv_troca_oleo, oficina_mecanica_disponivel=serv_ofic_mec, venda_gas_cozinha=serv_gas_cozinha, outros_servicos_disponibilidade=outros_servicos, valvula_retentora_vapor_disponibilidade=valv_ret_vap, valvula_retentora_vapor_estado_conservacao=radio_val_ret_vap, tanque_sub_parede_dupla_jaquetado=tanq_sub_par_dup_jaq, tanque_sub_parede_data_instalacao=tanq_sub_par_dup_jaq_data_inst, poco_monitoramento_disponibilidade=poco_mon, poco_monitoramento_estado_conservacao=radio_poco_mon, caneletas_ilhas_bombas_disponibilidade=can_ilha_bom, caneletas_ilhas_bombas_estado_conservacao=radio_can_ilha_bom, caneletas_perimetro_disponibilidade=can_per, caneletas_perimetro_estado_conservacao=radio_can_per, piso_concreto_alisado_disponibilidade=piso_alisado_bombas, piso_concreto_alisado_estado_conservacao=radio_piso_alisado_bombas, caneletas_interligadas_sao_disponibilidade=can_int_sao, caneletas_interligadas_sao_estado_conservacao=radio_can_int_sao, sistema_deteccao_vazamento_disponibilidade= sist_det_vaz, sistema_deteccao_vazamento_estado_conservacao=radio_sist_det_vaz, area_lavagem_piso_can_sao_disponibilidade=lav_vei_piso_can_sao, area_lavagem_piso_can_sao_estado_conservacao=radio_lav_vei_piso_can_sao, area_troca_oleo_piso_can_sao_disponibilidade=area_oleo_piso, area_troca_oleo_piso_can_sao_estado_conservacao=radio_area_oleo_piso, area_armazenamento_residuos_coberta_piso_disponibilidade=area_res_piso, area_armazenamento_residuos_coberta_piso_estado_conservacao=radio_area_res_piso, atendido_rede_publica_saneamento=at_red_pub_san, quantidade_tanques=quant_tanq_uni_select, capacidade_armazenamento=cap_tot_arm_txt, houve_sinistro_ultimos_anos=houve_sinistro, prejuizo_estimativa=prej_estim, data_sinistro=sinistro_data, ocorrencia=ocorrencia_text)

    laudo.save()

    # VINCULAR AS FOTOS NA PASTA DO USUÁRIO QUE COMECAM COM NOVO-

    postos = Posto.objects.order_by('nome')
    context = {'postos': postos}
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
