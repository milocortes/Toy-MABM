from engine_toy_model import Household
from engine_toy_model import Firm
from engine_toy_model import KFirm
from engine_toy_model import Goverment
from engine_toy_model import Bank
from engine_toy_model import BankigAccount
from engine_toy_model import Credito
from engine_toy_model import SSector
from engine_toy_model import compute_gini

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

import yaml

# Cargamos los parametros iniciales
with open(r'parametros_toy_model.yaml') as file:
    ci = yaml.load(file, Loader=yaml.FullLoader)

# Definimos diccionarios que almacenarán los resultados de cada simulacion
dict_tasa_desempleo = {}
dict_output_y = {}
dict_list_real_consum_efective = {}
dict_wage_w = {}
dict_list_cash_bill = {}
dict_list_avg_price = {}
dict_list_capital = {}
dict_list_gov_balance = {}
dict_list_profits = {}
dict_list_gini = {}
dict_list_demanda_gob = {}
dict_output_k_firms = {}
dict_subsistencia_sector= {}
dict_share_wages = {}
dict_share_profits = {}
dict_normalized_avg_price= {}

for simulacion in range(ci['simulacion']['experimentos']):
    print("###################################################")
    print("Simulación: ", simulacion)
    print("###################################################")

    for alpha in np.arange(ci['parametros']['alpha']['start'],ci['parametros']['alpha']['stop'],ci['parametros']['alpha']['step']):
        alpha=round(alpha,1)
        print("************************************************")
        print("Alpha: ",alpha)
        print("************************************************")
        # Precio promedio de las empresas de consumo
        avg_price = 0
        # Precio promedio de las empresas de capital
        k_average_price = 0
        # Costos Unitarios de mercado
        market_unit_cost = ci['parametros']['wageExogenous']/alpha
        # Definimos una lista que contendrá los hogares
        households= [Household(x) for x in range(ci['parametros']['n_households'])]

        # Definimos un diccionario con los hogares que no han sido empleados en ningún momento
        id_households_unemployment = {x:False for x in range(ci['parametros']['n_households'])}

        # Definimos una lista que contendrá las empresas productoras de bienes de consumo
        empresas = [Firm(x, (ci['parametros']['init_capital']/ci['parametros']['n_firms'])) for x in range(ci['parametros']['n_firms'])]

        # Definimos un diccionario con los id de las empresas productoras de bienes de consumo  que no han solicitado créditos
        id_c_firms = {x:False for x in range(ci['parametros']['n_firms'])}

        # Definimos una lista que contendrá las empresas productoras de bienes de capital
        kempresas = [KFirm(x) for x in range(ci['parametros']['n_firms_capital'])]

        # Definimos un diccionario con los id de las empresas productoras de bienes de capital que no han solicitado créditos
        id_k_firms = {x:False for x in range(ci['parametros']['n_firms_capital'])}

        # Instanciamos al gobierno
        goverment = Goverment()

        # Instanciamos un banco
        banco = Bank(ci['parametros']['interest_rate_anual'],ci['parametros']['capital_inicial_bancos'])

        # Instanciamos el sector de subsistencia
        ssector =SSector()

        # Tasa de desempleo
        unemployment_rate = 1
        # Tasa de desempleo promedio
        unemployment_rate_avg =1

        # Definimos listas que almacenarán los resultados
        tasa_desempleo = []
        output_y = []
        list_real_consum_efective = []
        wage_w = []
        list_cash_bill = []
        list_avg_price = []
        list_capital = []
        list_gov_balance = []
        list_profits = []
        list_gini = []
        list_demanda_gob = []
        output_k_firms = []
        subsistencia_sector=[]

        for i in range(ci['simulacion']['periodos']):
            print("###############################")
            print("Simulación: ", simulacion ,"alpha: ", alpha, "Periodo: ",str(i))
            ##### Comenzamos los tiks
            ##### Comenzamos los tiks
            ## Tick 0 --> El gobierno define su gasto real
            goverment.set_real_expenditure(ci['parametros']['gExogenous'])

            ## Tick 0 --> Las empresas definen su expectativa de producción y sus requerimientos de capital
            for empresa in empresas:
                empresa.deter_output_expec(ci['parametros']['nu'],ci['parametros']['delta_min'],ci['parametros']['delta_max'],avg_price,(ci['parametros']['gExogenous']/len(empresas)),i)
                empresa.actual_capital_requirements(ci['parametros']['kappa'], i)
            ## Tick 1 --> Las empresas de capital definen sus expectativas de producción
            for kempresa in kempresas:
                kempresa.deter_output_expec(ci['parametros']['delta_min'],ci['parametros']['delta_max'],k_average_price,i)

            ## Tick 2 --> Las empresas definen sus precios en base a un markup
            ##            sobre los costo unitarios pasados, establecido como un RW
            #             reflejando barreras a la entrada
            for empresa in empresas:
                empresa.set_prices(ci['parametros']['priceExogenous'],i, ci['parametros']['markup'], ci['parametros']['markupMin'], ci['parametros']['markupMax'], ci['parametros']['wageExogenous'],alpha,avg_price)

            ## Tick 3 --> Las empresas de capital definen sus precios.
            for kempresa in kempresas:
                kempresa.set_prices(i, ci['parametros']['markup'], ci['parametros']['markupMin'], ci['parametros']['markupMax'], ci['parametros']['wageExogenous'], alpha,k_average_price)

            ## Tick 4 --> Los trabajadores definen su salario de reserva y sus propensiones a consumir
            for household in households:
                household.set_reserve_wage(ci['parametros']['wageExogenous'],unemployment_rate,unemployment_rate_avg,i)
                household.set_propensity_cosumption(ci['parametros']['propension_ingreso'],ci['parametros']['propension_riqueza'])
                household.update_cash(banco)

            ## Tick 5 --> El gobierno comunica sus pedidos a las empresas de bienes de consumo
            goverment.define_demand_to_firms(empresas)
            demanda_gob =0
            for empresa in empresas:
                demanda_gob+=empresa.demand_by_goverment
            #print("Demanda de Gobierno ",str(demanda_gob))
            list_demanda_gob.append(demanda_gob)
            ## Tick 6 --> Los hogares definen su provedor de bienes de consumo
            for household in households:
                household.set_good_supplier(empresas)

            ## Tick 7 --> Las empresas de consumo definen su demanda de inversión y su proveedor de bienes de capital
            for empresa in empresas:
                empresa.set_real_demand(kempresas,ci['parametros']['parMatchingKFirms'],banco,i,ci['parametros']['anios_pagar']*4)

            ## Tick 8 --> Los hogares definen su demanda de bienes de consumo en términos reales y pagan su consumo
            for household in households:
                household.set_real_demand(empresas,banco,i)

            ## Tick 9 --> Las empresas de bienes de capital definen su requerimientos de trabajo, contratan trabajadores y pagan salarios
            for kempresa in kempresas:
                kempresa.deter_labor_required(alpha,households,i,banco,id_households_unemployment,ssector)

            ## Tick 10 --> La producción toma lugar en las empresas de capital
            for kempresa in kempresas:
                kempresa.produce(alpha,empresas,banco,i,ci['parametros']['anios_pagar']*4)

            producto_kfirm=0
            for kempresa in kempresas:
                producto_kfirm+=kempresa.output
            #print("Producto KFirms: ",str(producto_kfirm))
            output_k_firms.append(producto_kfirm)
            ## Tick 11 --> Las empresas de bienes de consumo definen su requerimientos de trabajo, contratan trabajadores y pagan salarios
            for empresa in empresas:
                empresa.deter_labor_required(ci['parametros']['kappa'],alpha,households,ci['parametros']['wageExogenous'],i,banco,id_households_unemployment,ssector)

            demanda_trabajo=0
            for empresa in empresas:
                demanda_trabajo+=len(empresa.employees)
            #print("Demanda trabajo: ",str(demanda_trabajo))

            ## Tick 11.a) --> Actualizamos los registros laborales
            for house in households:
                if house.employment== True:
                    house.employment_record[i] = True
                else:
                    house.employment_record[i] = False

            ## Tick 11.b) --> Si el trabajador no ha sido empleado en los últimos tres periodos, se incorporan al sector de subsistencia
            if i>2:
                for household in households:
                    if household.evalua_ssector(i):
                        ssector.incorpora_worker(household)

            ## Tick 12 --> La producción toma lugar en las empresas de consumo
            for empresa in empresas:
                empresa.produce(ci['parametros']['kappa'], households, goverment,banco,i,ci['parametros']['anios_pagar']*4)

            producto=0
            for empresa in empresas:
                producto+=empresa.output
            #print("Producto CFirms: ",str(producto))

            inventarios=0
            for empresa in empresas:
                inventarios+=empresa.inventories
            #print("Inventarios CFirms: ",str(inventarios))

            ## Tick 13 --> Se calculan las ganancias de las empresas de consumo
            for empresa in empresas:
                empresa.compute_total_cash()
                empresa.computed_gross_profits(i)

            ganancias=0
            for empresa in empresas:
                ganancias+= empresa.profits[i]
            list_profits.append(ganancias)
            #print("Ganancias: ",str(ganancias))

            ## Tick 14 --> Se calculan las ganancias de las empresas de capital
            for kempresa in kempresas:
                kempresa.compute_total_cash()
                kempresa.computed_gross_profits(i)

            ## Tick 15   ---> Se pagan impuestos
            ## Tick 15.a ---> Los hogares pagan impuestos
            for household in households:
                household.pay_taxes(goverment,ci['parametros']['tau'])

            salarios = 0
            trabajadores_empleados = 0
            for hogar in households:
                if hogar.employment==True:
                    salarios+=hogar.wage
                    trabajadores_empleados +=1
            wage_w.append(salarios)
            #print("Salarios: ",str(salarios))

            ## Tick 15.b ---> Las empresas de consumo pagan impuestos
            for empresa in empresas:
                empresa.computed_net_profits(goverment,ci['parametros']['tau'],i)

            cash_firms = 0
            for empresa in empresas:
                cash_firms+=empresa.cash[i]
            #print("Cash de empresas ", str(cash_firms))
            list_cash_bill.append(cash_firms)

            ## Tick 15.c ---> Las empresas de consumo pagan impuestos
            for kempresa in kempresas:
                kempresa.computed_net_profits(goverment,ci['parametros']['tau'],i)

            ## Tick 16 ---> El gobierno paga subsidios y calcula su déficit
            goverment.pay_subsidies(households)
            goverment.compute_deficit()
            list_gov_balance.append(goverment.balance)

            ## Tick 17 --> Las empresas de consumo calculan la inversión del siguiente periodo
            for empresa in empresas:
                empresa.compute_investment(ci['parametros']['omega_long_run'],ci['parametros']['depretiation_rate'],ci['parametros']['adjustment_costs'],ci['parametros']['weight_depretiation'],i)
                #print("Empresa ", str(empresa.id),". Capital en t ", str(empresa.capital[i]), ", Capital en t+1 ", str(empresa.capital[i+1]),". Inversión en t ", str(empresa.investment[i]))
            ## Tick 18 --> Las empresas de capital calculan sus inventarios
            for kempresa in kempresas:
                kempresa.compute_inventories_change(ci['parametros']['k_depretiation_rate'])

            ## Tick 19 --> El banco calcula su tasa de interés sobre los préstamos
            banco.compute_capital_adequacy_ratio(i)
            banco.compute_interest_rate_loans(i+1,ci['parametros']['reserve_ratio'],ci['parametros']['interest_rate_bc'])
            ### Validamos lo resultados

            real_consum_efective = 0
            real_consum_feasible = 0

            for hogar in households:
                real_consum_efective += hogar.real_consum_efective
                real_consum_feasible += hogar.real_consum_feasible

            list_real_consum_efective.append(real_consum_efective)
            #print("Consumo Real Efectivo: ",str(real_consum_efective))
            #print("Consumo Real Factible: ",str(real_consum_feasible))


            ## Calculamos el porcentaje de trabajadores en el sector de subsistencia
            subsistencia_sector.append(len(ssector.workers)/len(households))

            desempleados=0

            for hogares in households:
                if hogares.employment==False:
                    desempleados+=1
            #print("Desempleados ", str(desempleados))
            unemployment_rate = (desempleados-len(ssector.workers))/len(households)
            tasa_desempleo.append(unemployment_rate)
            unemployment_rate_avg = np.mean(tasa_desempleo)

            producto = 0
            for firm in empresas:
                producto+=firm.output

            output_y.append(producto)

            ## Calculamos los costos unitarios de mercado
            wage_bill_total = 0

            for empresa in empresas:
                wage_bill_total += empresa.wage_bill[i]

            market_unit_cost= wage_bill_total/((len(households)-desempleados)*alpha)
            #print("Los costos unitarios de mercado son ", str(market_unit_cost))
            ## Calculamos el precio promedio de las empresas de consumo
            avg_price_sum = 0
            for empresa in empresas:
                avg_price_sum += empresa.price

            avg_price = avg_price_sum /len(empresas)
            list_avg_price.append(avg_price)

            capital_total = 0
            for empresa in empresas:
                capital_total += empresa.capital[i]

            list_capital.append(capital_total)

            ## Calculamos el precio promedio de las empresas de capital
            k_average_price_sum = 0

            for kempresa in kempresas:
                k_average_price_sum += kempresa.price

            k_average_price= k_average_price_sum /len(kempresas)
            #print("**************************")
            #print("precio promedio de las empresas de capital ", str(k_average_price))
            # Calculamos el gini en hogares
            list_gini.append(compute_gini(households))

        #### Agregamos los resultados de la simulacion a los diccionarios
        index_time=[x for x in range(ci['simulacion']['periodos']) ]
        dict_tasa_desempleo[(simulacion,alpha)]=dict(zip(index_time,tasa_desempleo))
        dict_output_y[(simulacion,alpha)]=dict(zip(index_time,output_y))
        dict_list_real_consum_efective[(simulacion,alpha)]=dict(zip(index_time,list_real_consum_efective))
        dict_wage_w[(simulacion,alpha)]=dict(zip(index_time,wage_w))
        dict_list_cash_bill[(simulacion,alpha)]=dict(zip(index_time,list_cash_bill))
        dict_list_avg_price[(simulacion,alpha)]=dict(zip(index_time,list_avg_price))
        dict_list_capital[(simulacion,alpha)]=dict(zip(index_time,list_capital))
        dict_list_gov_balance[(simulacion,alpha)]=dict(zip(index_time,list_gov_balance))
        dict_list_profits[(simulacion,alpha)]=dict(zip(index_time,list_profits))
        dict_list_gini[(simulacion,alpha)]=dict(zip(index_time,list_gini))
        dict_list_demanda_gob[(simulacion,alpha)]=dict(zip(index_time,list_demanda_gob))
        dict_output_k_firms[(simulacion,alpha)]=dict(zip(index_time,output_k_firms))
        dict_subsistencia_sector[(simulacion,alpha)]=dict(zip(index_time,subsistencia_sector))

        ## Sumamos las ganacias y los salarios
        total_gpd = [(x+y)for x,y in zip(wage_w,list_profits)]
        ## Obtenemos los shares
        share_wages = [(x/y) for x,y in zip(wage_w,total_gpd)]
        share_profits = [(x/y) for x,y in zip(list_profits,total_gpd)]
        ## Normalizamos los precios promedio
        min_avg_price= np.min(list_avg_price)
        max_avg_price= np.max(list_avg_price)
        normalized_avg_price= [((x-min_avg_price)/(max_avg_price-min_avg_price)) for x in list_avg_price]

        ## Guardamos los shares de salarios y ganancias, así como los precios normalizados en sus diccionarios
        dict_share_wages[(simulacion,alpha)]= dict(zip(index_time,share_wages))
        dict_share_profits[(simulacion,alpha)]= dict(zip(index_time,share_profits))
        dict_normalized_avg_price[(simulacion,alpha)]= dict(zip(index_time,normalized_avg_price))


#### Guardamos los resultados en csv
path = os.getcwd()+"/data"

pd.DataFrame.from_dict(dict_tasa_desempleo,orient='index').to_csv(os.path.join(path,'tasa_desempleo.csv'), index_label = ['sim','alpha'])
pd.DataFrame.from_dict(dict_output_y,orient='index').to_csv(os.path.join(path,'producto.csv'), index_label = ['sim','alpha'])
pd.DataFrame.from_dict(dict_list_real_consum_efective,orient='index').to_csv(os.path.join(path,'consumo_real_efectivo.csv'), index_label = ['sim','alpha'])
pd.DataFrame.from_dict(dict_wage_w,orient='index').to_csv(os.path.join(path,'salarios.csv'), index_label = ['sim','alpha'])
pd.DataFrame.from_dict(dict_list_cash_bill,orient='index').to_csv(os.path.join(path,'cash_bill.csv'), index_label = ['sim','alpha'])
pd.DataFrame.from_dict(dict_list_avg_price,orient='index').to_csv(os.path.join(path,'precio_promedio.csv'), index_label = ['sim','alpha'])
pd.DataFrame.from_dict(dict_list_capital,orient='index').to_csv(os.path.join(path,'capital.csv'), index_label = ['sim','alpha'])
pd.DataFrame.from_dict(dict_list_gov_balance,orient='index').to_csv(os.path.join(path,'balance_gobierno.csv'), index_label = ['sim','alpha'])
pd.DataFrame.from_dict(dict_list_profits,orient='index').to_csv(os.path.join(path,'ganancias.csv'), index_label = ['sim','alpha'])
pd.DataFrame.from_dict(dict_list_gini,orient='index').to_csv(os.path.join(path,'gini.csv'), index_label = ['sim','alpha'])
pd.DataFrame.from_dict(dict_list_demanda_gob,orient='index').to_csv(os.path.join(path,'demanda_gobierno.csv'), index_label = ['sim','alpha'])
pd.DataFrame.from_dict(dict_output_k_firms,orient='index').to_csv(os.path.join(path,'producto_sector_k.csv'), index_label = ['sim','alpha'])
pd.DataFrame.from_dict(dict_subsistencia_sector,orient='index').to_csv(os.path.join(path,'porcentaje_pobocup_sectorsubs.csv'), index_label = ['sim','alpha'])
pd.DataFrame.from_dict(dict_share_wages,orient='index').to_csv(os.path.join(path,'share_wage.csv'), index_label = ['sim','alpha'])
pd.DataFrame.from_dict(dict_share_profits,orient='index').to_csv(os.path.join(path,'share_profits.csv'), index_label = ['sim','alpha'])
pd.DataFrame.from_dict(dict_normalized_avg_price,orient='index').to_csv(os.path.join(path,'normalized_avg_price.csv'), index_label = ['sim','alpha'])
