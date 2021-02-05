import random
import math

class Firm(object):
    """docstring for Firm."""

    def __init__(self,id,capital):
        self.id = id
        self.price = 0
        self.capital = {0:capital}
        self.desired_capital = {}
        self.desired_employment = 0
        self.demand_by_households = 0
        self.demand_by_goverment = 0
        self.cash = {0:0}
        self.total_cash = 0
        self.cash_by_goverment = 0
        self.cash_by_households = 0
        self.good_supplier = 0
        self.price_supplier = 0
        self.employees = []
        self.wage_bill = {0:0}
        self.output = 0
        self.expected_output = 0
        self.inventories = 0
        self.rcapacity_util = {}
        self.profits = {0:0}
        self.total_demand = 0
        self.supply_constraint = 0
        self.id_consumers = {}
        self.investment = {0:0}

    def deter_output_expec(self,nu,delta_min,delta_max,average_price,goverment_expenditure,time):
        if time ==0:
            self.expected_output = goverment_expenditure + 10
        else:
            if (self.inventories <= delta_min) and (self.price >= average_price):
                self.expected_output = self.output *(1 + nu)
                #print("La expectativa de producto es ",str(self.expected_output)," empresa ", str(self.id))
            elif (self.inventories > delta_max) and (self.price < average_price):
                self.expected_output = self.output *(1 - nu)
                #print("La expectativa de producto es ",str(self.expected_output)," empresa ", str(self.id))
            else:
                self.expected_output = self.output
                #print("La expectativa de producto es ",str(self.expected_output)," empresa ", str(self.id))

    def actual_capital_requirements(self, capital_productivity,time):
        if time ==0:
            #print("El capital actual es ", str(self.capital[time]))

            # Definimos el capital deseado para alcanzar el producto esperado
            self.desired_capital[time] = self.expected_output/capital_productivity
            #print("El capital deseado en tiempo ", str(time), "es ", str(self.desired_capital[time]))
            # Tenemos dos opciones:
            #   * El capital deseado es mayor que el capital actual
            if self.desired_capital[time] >= self.capital[time]:
                self.rcapacity_util[time] = 1
            #   * El capital deseado es menor que el capital actual
            if self.desired_capital[time] < self.capital[time]:
                self.rcapacity_util[time] = self.desired_capital[time] /self.capital[time]
        else:
            #print("El capital actual es ", str(self.capital[time-1]))

            # Definimos el capital deseado para alcanzar el producto esperado
            self.desired_capital[time] = self.expected_output/capital_productivity
            #print("El capital deseado en tiempo ", str(time), "es ", str(self.desired_capital[time]))
            # Tenemos dos opciones:
            #   * El capital deseado es mayor que el capital actual
            if self.desired_capital[time] >= self.capital[time-1]:
                self.rcapacity_util[time] = 1
            #   * El capital deseado es menor que el capital actual
            if self.desired_capital[time] < self.capital[time-1]:
                self.rcapacity_util[time] = self.desired_capital[time] /self.capital[time-1]

    def set_prices(self,price_exogenous,time, markup, markup_min, markup_max, wage_exogenous, labor_productivity,market_unit_cost):

        if time == 0:

            markup = markup * (1+random.uniform(-0.05,0.05))

            if markup > markup_max :
                markup = markup_max
            elif markup < markup_min:
                markup = markup_min
            else:
                markup = markup

            unit_cost = wage_exogenous / labor_productivity
            self.price = (1+markup)* unit_cost

        else:
            if len(self.employees) > 0 and self.wage_bill[time-1] > 0:
                #print("Wage bill ", str(self.wage_bill))
                #print("# empleados ", str(len(self.employees)))
                unit_cost = self.wage_bill[time-1] / (len(self.employees) * labor_productivity)
                if  unit_cost > 0 :
                    #print("Los costos unitarios son ", str(unit_cost))
                    self.price = (1+markup)* unit_cost
                    #print("El costo unitario es ", str(unit_cost))
                    #print("El precio a ofertar ", str(self.price))
            else:
                unit_cost = market_unit_cost
                self.price = (1+markup)* unit_cost


    def receive_goverment_order(self,quantity):
        self.demand_by_goverment +=  quantity

    def receive_household_order(self,id,quantity):
        self.id_consumers[id] = quantity
        self.demand_by_households +=  quantity

    def receive_goverment_pay(self,quantity_cash):
        self.cash_by_goverment +=  quantity_cash

    def give_back_goverment_pay(self,goverment,quantity,nominal_quantity):
        goverment.real_expenditure_efective = goverment.real_expenditure - quantity
        goverment.nominal_expenditure_efective = goverment.nominal_expenditure - nominal_quantity
        self.cash_by_goverment -= nominal_quantity

    def receive_household_pay(self,quantity):
        self.cash_by_households +=  quantity_cash

    def deter_labor_required(self,capital_productivity,labor_productivity,households,wage_param,time,banco,id_households_unemployment,ssector):
        # Calculamos la razón capital trabajo
        capital_labor_ratio= capital_productivity / labor_productivity
        # Definimos los requerimientos laborales
        #print("Capital deseado ", str(self.desired_capital[time]))
        #print("Capital actual ", str(self.capital[time]))
        self.desired_employment = math.floor(min(self.desired_capital[time] * capital_labor_ratio, self.capital[time] * capital_labor_ratio))
        labor_required =  math.floor(min(self.desired_capital[time] * capital_labor_ratio, self.capital[time] * capital_labor_ratio))
        #print("Necesitamos ",str(labor_required)," y tenemos ", str(len(self.employees)), " empresa ", str(self.id))
        # Definimos la demanda laboral para este periodo
        labor_demand = labor_required -len(self.employees)

        # Si hay exceso de mano de obra, se despiden trabajadores
        if labor_demand == 0:
            #print("Requerimientos laborales cubiertos")
            pass
        elif labor_demand < 0:
            # Seleccionamos de forma aleatoria los trabajadores a despedir
            while labor_demand!=0:
                id_worker = math.floor(random.uniform(0,len(self.employees)))
                # Cambiamos el estatus a desempleado del trabajador
                self.employees[id_worker].employment=False
                # Eliminamos al trabajador de la lista de empleados
                del self.employees[id_worker]
                labor_demand = labor_required -len(self.employees)
        else:
            # Interactuamos en el mercado laboral para contratar trabajadores
            for worker in households:
                if worker.employment == False:
                    # Cambiamos el estatus del trabajador a empleado
                    worker.employment = True
                    # Si está en el sector de subsistencia, lo removemos del diccionario
                    if worker.id in ssector.workers:
                        ssector.remueve_worker(worker)
                    worker.employer_index = self.id
                    self.employees.append(worker)
                    if (worker.id in id_households_unemployment):
                        worker.open_banking_account(banco,time)
                        worker.add_to_account(banco,time)
                        del id_households_unemployment[worker.id]
                    labor_demand = labor_required -len(self.employees)
                if labor_demand ==0:
                    break


    def produce(self,capital_productivity,households, goverment,banco,time,anios_pagar):
        #print("Capacidad a ocupar ",str( self.rcapacity_util[time]), " tiempo ", str(time))
        #print("Capital ", str(self.capital[time]), " tiempo ", str(time))
        self.output =  self.rcapacity_util[time] * capital_productivity * self.capital[time]
        #print("El producto es ",str(math.floor(self.output)))
        # Temporalmente el producto se guarda como inventarios
        self.inventories = self.output
        #print("Inventarios: ", str(self.inventories), "Demanda del Gobierno: ", str(self.demand_by_goverment))

        if self.inventories >= self.demand_by_goverment:
            #print("Cumplimos con la demanda del Gobierno")
            self.inventories -= self.demand_by_goverment
            self.demand_by_goverment -= self.demand_by_goverment
        self.demand_by_goverment -= self.demand_by_goverment
        ### El producto se entrega a los demandantes
        #print("Inventarios: ", str(self.inventories), "Demanda hogares: ", str(self.demand_by_households))
        for k in self.id_consumers:
            if self.inventories >= self.id_consumers[k]:
                #print("Se puede cumplir la demanda")
                self.inventories-=self.id_consumers[k]
                self.demand_by_households -= self.id_consumers[k]
            else:
                # En caso que no se cumplan las demandas de los consumidores
                # se devuelve su compra
                #print("No se satisfizo la demanda al cliente ", str(k))
                #print("Inventarios: ", str(self.inventories), " Demanda: ", str(self.id_consumers[k]))
                #print("Tenemos que devolver ", str(self.id_consumers[k]))
                #print("El real_consum_feasible es ", str(households[k].real_consum_feasible))
                quantity = self.id_consumers[k]
                nominal_quantity = quantity *self.price
                self.demand_by_households -= quantity
                households[k].real_consum_efective -= quantity
                #print("El real_consum_efective es ", str(households[k].real_consum_efective))
                households[k].cash += nominal_quantity
                self.cash_by_households -= nominal_quantity

        # Sumamos el cash proveniente del govierno y de los trabajadores
        self.cash[time] = self.cash_by_goverment + self.cash_by_households
        # Restamos del output los inventarios
        # self.output -= self.inventories
        # Reseteamos el diccionario
        self.id_consumers= {}

        #print("El cash actual es ", str(self.cash))
        #self.give_back_goverment_pay(goverment,self.demand_by_goverment,self.demand_by_goverment* self.price)
        ## Se pagan salarios
        # Reseteamos la nómina de salarios de este periodo
        self.wage_bill[time]=0

        deuda_nomina = 0

        for worker in self.employees:
            if self.cash[time] >= worker.wage:
                worker.wage_pay_cash = True
                worker.gross_income = worker.wage
                self.wage_bill[time] += worker.wage
                self.cash[time] -= worker.wage
                worker.saving = (worker.wage*(1 - worker.pc_income))
                worker.add_to_account(banco,time)
            else:
                deuda_nomina += worker.wage
        if deuda_nomina > 0:
            #print("Necesitamos solicitar crédito para pagar salarios")
            actual_interest_rate_loans_key=list(banco.interest_rate_loans)[-1]
            self.solicita_credito_nomina(banco,deuda_nomina,time,anios_pagar,banco.interest_rate_loans[actual_interest_rate_loans_key])
            # En caso que no se hayan pagado los salarios con cash, la empresa solicita crédito
            for worker in self.employees:
                if worker.wage_pay_cash != True:
                    worker.gross_income = worker.wage
                    worker.cash += worker.wage
                    self.wage_bill[time] += worker.wage

    def computed_gross_profits(self,time):
        # Definimos la demanda total (real) al sumar las demandas del gobierno y de los hogares
        self.profits[time] = (self.output * self.price) -self.wage_bill[time]

    def computed_net_profits(self,goverment,tax_rate,time):
        tax_amount = tax_rate*self.profits[time]
        self.profits[time]-=max(tax_amount,0)
        # Se pagan impuestos al gobierno
        goverment.tax_profits+= tax_amount

    def calc_average_capital(self,weight_depretiation,time):
        if time == 0 or time == 1:
            return self.capital[time]
        else:
            t_2_average_capital = self.calc_average_capital(weight_depretiation,time-2)
            t_1_average_capital = weight_depretiation *t_2_average_capital +(1-weight_depretiation) * self.rcapacity_util[time-1]*self.capital[time-1]

            return t_1_average_capital

    def calculate_capital_next_period(self,rcapacity_util_long_run,depretiation_rate,adjustment_costs,weight_depretiation,time):
        if time ==0:
            self.capital[time+1] = (1-depretiation_rate) * self.capital[time]
        else:
            coeficient = ((1/rcapacity_util_long_run)+(depretiation_rate/adjustment_costs))
            t_1_avg_capital = self.calc_average_capital(weight_depretiation,time-1)

            self.capital[time+1]= coeficient * t_1_avg_capital - (depretiation_rate* self.rcapacity_util[time] * self.capital[time])
            #print("El capital para el periodo t+1 es ", str(self.capital[time+1]))

    def compute_investment(self,rcapacity_util_long_run,depretiation_rate,adjustment_costs,weight_depretiation,time):
        if time ==0:
            self.capital[time+1] = (1-depretiation_rate) * self.capital[time]
            self.investment[time+1]= 0
        else:
            coeficient = ((1/rcapacity_util_long_run)+(depretiation_rate/adjustment_costs))
            self.capital[time] = (1-depretiation_rate) * self.capital[time]
            t_1_avg_capital = self.calc_average_capital(weight_depretiation,time-1)
            #print("La empresa ",str(self.id)," del C-sector tiene un consumo promedio de capital ", str(coeficient*t_1_avg_capital), " y el capital actual es ", str(self.capital[time]))
            self.investment[time+1]= (coeficient*t_1_avg_capital) - self.capital[time]
            #print("La empresa ",str(self.id)," del C-sector pretende invertir en t+1", str(self.investment[time+1]))
            self.capital[time+1] =  self.capital[time]

    def open_banking_account_nomina(self,banco,time):
        banco.cuentas_C_sector[self.id]= BankigAccount(self.id, time)

    def open_banking_account_inversion(self,banco,time):
        banco.cuentas_investment_C_sector[self.id]= BankigAccount(self.id, time)

    def solicita_credito_nomina(self,banco,amount,time,anios,interest_rate):
        ## Si el hogar no tiene una cuenta bancaria, se realiza la apertura
        if not(self.id in banco.cuentas_C_sector):
            self.open_banking_account_nomina(banco,time)
        ## El hogar solicita el crédito, calcula el pago, el valor final y la deuda total
        banco.cuentas_C_sector[self.id].creditos[time]=Credito(time,amount,anios,interest_rate)
        banco.cuentas_C_sector[self.id].creditos[time].calcula_pago()
        banco.cuentas_C_sector[self.id].creditos[time].calcula_vf()

        ## El banco agrega la cantidad prestada a sus activos
        banco.loans += amount

    def solicita_credito_inversion(self,banco,amount,time,anios,interest_rate):
        ## Si el hogar no tiene una cuenta bancaria, se realiza la apertura
        if not(self.id in banco.cuentas_investment_C_sector):
            self.open_banking_account_inversion(banco,time)
        ## El hogar solicita el crédito, calcula el pago, el valor final y la deuda total
        banco.cuentas_investment_C_sector[self.id].creditos[time]=Credito(time,amount,anios,interest_rate)
        banco.cuentas_investment_C_sector[self.id].creditos[time].calcula_pago()
        banco.cuentas_investment_C_sector[self.id].creditos[time].calcula_vf()

        ## El banco agrega la cantidad prestada a sus activos
        banco.loans += amount

    def set_real_demand(self,kfirmas,parMatchingKFirms,banco,time,anios_pagar):
        self.cash[time]=0
        self.set_good_price_supplier(kfirmas,parMatchingKFirms)
        self.compute_total_cash()
        # El hogar ordena su pedido a la firma
        if self.investment[time] > 0:
            #print("Tenemos que pagar por la inversión ", str(self.investment[time]*self.price_supplier)," y tenemos en cash ", str(self.cash))
            # Evaluamos si la empresa esta en condición de solventar la inversión con recursos propios
            if (self.investment[time]*self.price_supplier) <=  self.total_cash:
                kfirmas[self.good_supplier].receive_cfirm_order(self.id,self.investment[time])
                #print("La empresa ",str(self.id)," del C-sector pretende consumir bienes de capital en t+1", str(self.investment[time]))
                # La empresa de consumo paga el pedido a la empresa de capital
                self.pay_consumption(time)
                self.pay_to_firm(kfirmas,self.investment[time])
            else:
                print("Necesitamos solicitar crédito para pagar inversión")
                actual_interest_rate_loans_key=list(banco.interest_rate_loans)[-1]
                self.solicita_credito_inversion(banco,self.investment[time],time,anios_pagar,banco.interest_rate_loans[actual_interest_rate_loans_key])
                #self.cash[time]+=self.investment[time]
                kfirmas[self.good_supplier].receive_cfirm_order(self.id,self.investment[time])
                #print("La empresa ",str(self.id)," del C-sector pretende consumir bienes de capital en t+1", str(self.investment[time]))
                # La empresa de consumo paga el pedido a la empresa de capital
                #self.pay_consumption(time)
                self.pay_to_firm(kfirmas,self.investment[time])

    def pay_consumption(self,time):
        self.total_cash -= (self.investment[time] * self.price)

    def pay_to_firm(self,firms,amount):
        for firm in firms:
            if firm.id ==self.good_supplier:
                nominal_amount = amount * self.price_supplier
                firm.receive_cfirm_pay(nominal_amount)

    def set_good_price_supplier(self, firms,parMatchingKFirms):
        ids=[]
        ids_len = 0

        while ids_len !=parMatchingKFirms:
            id = math.ceil(random.uniform(0,len(firms)-1))
            ids.append(id)
            ids_len = len(set(ids))

        minimum_price = 10000000
        id_minimum_price = 0

        for id in ids:
            if firms[id].price < minimum_price :
                minimum_price = firms[id].price
                id_minimum_price = id

        self.good_supplier = id_minimum_price
        self.price_supplier = minimum_price

    def compute_total_cash(self):
        self.total_cash=sum(self.cash.values())

class KFirm(object):
    """docstring for KFirm."""


    def __init__(self,id):
        self.id = id
        self.price = 0
        self.desired_employment = 0
        self.demand_by_cfirm = 0
        self.cash = {0:0}
        self.total_cash = 0
        self.cash_by_cfirm = 0
        self.employees = []
        self.wage_bill = {0:0}
        self.output = 0
        self.expected_output = 0
        self.inventories = 0
        self.acumulated_change_inventories = 0
        self.actual_change_inventories = 0
        self.profits = {0:0}
        self.id_consumers = {}

    def deter_output_expec(self,delta_min,delta_max,average_price,time):
        ajuste = 0.1
        if time ==0:
            self.expected_output = 10
        else:
            if self.actual_change_inventories <= delta_min and self.price < average_price:
                actual_output = self.output
                #print("**************************")
                #print("El producto anterior fue ", str(actual_output))
                adjustment_output = actual_output + (ajuste*(-1 * self.actual_change_inventories)) - self.inventories
                self.expected_output = adjustment_output + self.inventories
                #print("La expectativa de producto es ",str(self.expected_output)," empresa ", str(self.id), " en el K-sector")
            elif (self.actual_change_inventories > delta_max) and (self.price > average_price):
                actual_output = self.output
                #print("El producto anterior fue ", str(actual_output))
                #print("El self.actual_change_inventories es ",str(self.actual_change_inventories))
                #print("Los inventarios acumulados son ", str(self.inventories))
                adjustment_output = actual_output - (ajuste * self.actual_change_inventories) - self.inventories
                self.expected_output = adjustment_output + self.inventories
                #print("La expectativa de producto es ",str(self.expected_output)," empresa ", str(self.id)," en el K-sector")
            else:
                actual_output = self.output
                #print("El producto anterior fue ", str(actual_output))
                #print("La expectativa de producto es ",str(self.expected_output)," empresa ", str(self.id))

    def set_prices(self,time, markup, markup_min, markup_max, wage_exogenous, labor_productivity,average_price):

        if time == 0:

            markup = markup * (1 + random.uniform(-0.05,0.05))

            if markup > markup_max :
                markup = markup_max
            elif markup < markup_min:
                markup = markup_min
            else:
                markup = markup

            unit_cost = wage_exogenous / labor_productivity
            #self.price = (1 + markup)* unit_cost
            self.price = random.uniform(0.1,0.2)

        else:
            if self.actual_change_inventories <= 0 and self.price < average_price:
                actual_price = self.price
                self.price = actual_price *(1 + random.uniform(0,0.1))
            elif self.actual_change_inventories > 0 and self.price > average_price:
                actual_price = self.price
                self.price = actual_price *(1 - random.uniform(0,0.1))

    def receive_cfirm_order(self,id,quantity):
        self.id_consumers[id] = quantity
        self.demand_by_cfirm +=  quantity

    def receive_cfirm_pay(self,quantity_cash):
        self.cash_by_cfirm +=  quantity_cash

    def deter_labor_required(self,labor_k_sector_productivity,households,time,banco,id_households_unemployment,ssector):
        # Definimos los requerimientos laborales
        self.desired_employment = math.floor(self.expected_output/labor_k_sector_productivity)
        labor_required =  self.desired_employment
        #print("Necesitamos ",str(labor_required)," y tenemos ", str(len(self.employees)), " empresa en el K-sector ", str(self.id))
        # Definimos la demanda laboral para este periodo
        labor_demand = labor_required -len(self.employees)

        # Si hay exceso de mano de obra, se despiden trabajadores
        if labor_demand == 0:
            pass
            #print("Requerimientos laborales cubiertos")
        elif labor_demand < 0:
            # Seleccionamos de forma aleatoria los trabajadores a despedir
            while labor_demand!=0:
                id_worker = math.floor(random.uniform(0,len(self.employees)))
                # Cambiamos el estatus a desempleado del trabajador
                self.employees[id_worker].employment=False
                # Eliminamos al trabajador de la lista de empleados
                del self.employees[id_worker]
                labor_demand = labor_required -len(self.employees)
        else:
            # Interactuamos en el mercado laboral para contratar trabajadores
            for worker in households:
                if worker.employment == False:
                    # Cambiamos el estatus a empleado
                    worker.employment = True
                    # Si está en el sector de subsistencia, lo removemos del diccionario
                    if worker.id in ssector.workers:
                        ssector.remueve_worker(worker)
                    worker.employer_index = self.id
                    self.employees.append(worker)
                    if (worker.id in id_households_unemployment):
                        worker.open_banking_account(banco,time)
                        worker.add_to_account(banco,time)
                        del id_households_unemployment[worker.id]

                    labor_demand = labor_required -len(self.employees)
                if labor_demand ==0:
                    break

    def produce(self,labor_k_sector_productivity,empresas,banco,time,anios_pagar):
        #print("Capacidad a ocupar ",str( self.rcapacity_util[time]), " tiempo ", str(time))
        #print("Capital ", str(self.capital[time]), " tiempo ", str(time))
        self.output =  labor_k_sector_productivity * len(self.employees)
        #print("El producto es ",str(math.floor(self.output)))
        # Temporalmente el producto se guarda como inventarios
        self.actual_change_inventories = math.floor(self.output)

        ### El producto se entrega a los demandantes
        #print("Inventarios: ", str(self.inventories), "Demanda c-sector: ", str(self.demand_by_cfirm))
        for k in self.id_consumers:
            if self.actual_change_inventories >= self.id_consumers[k]:
                #print("Se puede cumplir la demanda")
                self.actual_change_inventories-=self.id_consumers[k]
                self.demand_by_cfirm -= self.id_consumers[k]
                empresas[k].capital[time] = empresas[k].capital[time]+self.id_consumers[k]
            else:
                # En caso que no se cumplan las demandas de los consumidores
                # se devuelve su compra
                #print("No se satisfizo la demanda al cliente ", str(k))
                #print("Inventarios: ", str(self.inventories), " Demanda: ", str(self.id_consumers[k]))
                #print("Tenemos que devolver ", str(self.id_consumers[k]))
                #print("El real_consum_feasible es ", str(households[k].real_consum_feasible))
                quantity = self.id_consumers[k]
                nominal_quantity = quantity *self.price
                self.demand_by_cfirm -= quantity
                empresas[k].capital[time] = empresas[k].capital[time]
                #print("El real_consum_efective es ", str(households[k].real_consum_efective))
                empresas[k].cash[time] += nominal_quantity
                self.cash_by_cfirm -= nominal_quantity


        # Sumamos el cash proveniente del govierno y de los trabajadores
        self.cash[time] = self.cash_by_cfirm
        #print("Cash de c-sectot ",str(self.cash[time]))
        # Restamos del output los inventarios
        # self.output -= self.inventories
        # Reseteamos el diccionario
        self.id_consumers= {}

        #print("El cash actual es ", str(self.cash))
        #self.give_back_goverment_pay(goverment,self.demand_by_goverment,self.demand_by_goverment* self.price)
        ## Se pagan salarios
        # Reseteamos la nómina de salarios de este periodo
        self.wage_bill[time]=0

        deuda_nomina = 0

        for worker in self.employees:
            if self.cash[time] >= worker.wage:
                worker.wage_pay_cash = True
                worker.gross_income = worker.wage
                self.wage_bill[time] += worker.wage
                self.cash[time] -= worker.wage
                worker.saving = (worker.wage*(1 - worker.pc_income))
                worker.add_to_account(banco,time)
            else:
                deuda_nomina += worker.wage
        if deuda_nomina > 0:
            #print("Necesitamos solicitar crédito para pagar salarios")
            actual_interest_rate_loans_key=list(banco.interest_rate_loans)[-1]
            self.solicita_credito_nomina(banco,deuda_nomina,time,anios_pagar,banco.interest_rate_loans[actual_interest_rate_loans_key])
            # En caso que no se hayan pagado los salarios con cash, la empresa solicita crédito
            for worker in self.employees:
                if worker.wage_pay_cash != True:
                    worker.gross_income = worker.wage
                    worker.cash += worker.wage
                    self.wage_bill[time] += worker.wage

            """
                else:
                    worker.gross_income = self.cash
                    worker.cash += self.cash
                    self.wage_bill += self.cash
                    self.cash -= 0
            """
    def computed_gross_profits(self,time):
        # Definimos la demanda total (real) al sumar las demandas del gobierno y de los hogares
        self.profits[time] = (self.output * self.price) -self.wage_bill[time]

    def computed_net_profits(self,goverment,tax_rate,time):
        tax_amount = tax_rate*self.profits[time]
        self.profits[time]-=max(tax_amount,0)
        # Se pagan impuestos al gobierno
        goverment.tax_profits+= tax_amount

    def open_banking_account(self,banco,time):
        banco.cuentas_K_sector[self.id]= BankigAccount(self.id, time)

    def solicita_credito_nomina(self,banco,amount,time,anios,interest_rate):
        ## Si el hogar no tiene una cuenta bancaria, se realiza la apertura
        if not(self.id in banco.cuentas_K_sector):
            self.open_banking_account(banco,time)
        ## El hogar solicita el crédito, calcula el pago, el valor final y la deuda total
        banco.cuentas_K_sector[self.id].creditos[time]=Credito(time,amount,anios,interest_rate)
        banco.cuentas_K_sector[self.id].creditos[time].calcula_pago()
        banco.cuentas_K_sector[self.id].creditos[time].calcula_vf()

        ## El banco agrega la cantidad prestada a sus activos
        banco.loans += amount

    def compute_inventories_change(self,ksector_depretiation):
        #print("*********************************")
        #print("Calculamos los cambios en invetarios en la empresa K ",str(self.id))
        #print("Producto actual ", str(self.output))
        #print("Demanda de C-empresas ",str(self.demand_by_cfirm))
        #print("Inventarios actuales ",str(self.inventories))
        #print("Cambio actual en inventarios ", str(self.actual_change_inventories))
        actual_inventories = self.inventories
        self.inventories = (actual_inventories + self.actual_change_inventories) * (1 - ksector_depretiation)
        #print("Inventarios t+1 ",str(self.inventories))
        self.acumulated_change_inventories = self.inventories - actual_inventories
        #print("Cambio en los inventarios acumulados ", str(self.acumulated_change_inventories))

    def compute_total_cash(self):
        self.total_cash=sum(self.cash.values())

class Household(object):
    """docstring for Household."""

    def __init__(self, id):
        self.id = id
        self.wage = 0
        self.cash = 0
        self.employment = False
        self.employment_record ={0:False}
        self.employer_index = 0
        self.wage_pay_cash = False
        self.gross_income = 0
        self.disposable_income = 0
        self.good_supplier = 0
        self.pc_income = 0
        self.pc_wealth = 0
        self.real_demand_desired = 0
        self.demand_desired = 0
        self.consum_feasible = 0
        self.real_consum_feasible = 0
        self.real_consum_efective = 0
        self.real_income = 0
        self.real_wealth = 0
        self.saving = 0

    def set_reserve_wage(self,wage,unemployment_rate,unemployment_rate_avg,time):
        if time < 4:
            self.wage = (1 + random.uniform(-0.1,0.1))* wage
        else:
            ## Evaluamos las tasas de desempleo de los cuatro periodos anteriores
            periodos_desempleado = 0
            for i in range(1,5):
                if self.employment_record[time - i] == False:
                    periodos_desempleado+=1
            ## Ajustamos los salarios de reserva
            if periodos_desempleado > 2:
                actual_wage = self.wage
                self.wage = (1 + random.uniform(-0.03,0))* actual_wage
            elif (periodos_desempleado <=2) and (unemployment_rate <=0.01):
                actual_wage = self.wage
                self.wage = (1 + random.uniform(0,0.03))* actual_wage
            else:
                self.wage = (1 + random.uniform(-0.1,0.1))* wage

    def open_banking_account(self,banco,time):
        banco.cuentas_workers[self.id]= BankigAccount(self.id, time)

    def add_to_account(self,banco,time):
        banco.cuentas_workers[self.id].depositar(self.saving,time)

    def solicita_credito(self,banco,amount,time,anios,interest_rate):
        ## Si el hogar no tiene una cuenta bancaria, se realiza la apertura
        if not(self.id in banco.cuentas_workers):
            self.open_banking_account(banco,time)
        ## El hogar solicita el crédito, calcula el pago, el valor final y la deuda total
        banco.cuentas_workers[self.id].creditos[time]=Credito(time,amount,anios,interest_rate)
        banco.cuentas_workers[self.id].creditos[time].calcula_pago()
        banco.cuentas_workers[self.id].creditos[time].calcula_vf()

        ## El banco agrega la cantidad prestada a sus activos
        banco.loans += amount


    def set_good_supplier(self, firms):
        self.good_supplier = math.ceil(random.uniform(0,len(firms)-1))

    def set_propensity_cosumption(self,pc_income,pc_wealth):
        self.pc_income = pc_income
        self.pc_wealth = pc_wealth

    def set_real_demand(self,firmas,banco,time):
        provider_price = self.get_provider_price(firmas)
        if self.disposable_income < 0:
            print("El hogar tiene ingreso disponible negativo")
        self.real_income = self.disposable_income/provider_price
        self.real_wealth =  self.cash/provider_price
        self.real_demand_desired= math.floor((self.pc_income *(self.real_income)) + (self.pc_wealth *(self.real_wealth)))
        self.demand_desired = self.real_demand_desired * provider_price
        self.consum_feasible = min(self.demand_desired,self.cash)
        self.real_consum_feasible = min(self.real_demand_desired, math.floor(self.real_wealth))
        self.real_consum_efective = min(self.real_demand_desired, math.floor(self.real_wealth))

        #print("Ingreso real ",str(self.real_income))
        #print("Riqueza real ",str(self.real_wealth))
        #print("El hogar ",str(self.id), " desea a consumir ", self.real_demand_desired)
        #print("El hogar ",str(self.id), " va a consumir ", self.real_consum_efective)
        # El hogar ordena su pedido a la firma
        if self.real_consum_feasible > 0:
            self.order_to_firms(firmas,self.id,self.real_consum_feasible)
            # El hogar paga el pedido a la firma
            self.pay_consumption(banco,time)

    def pay_consumption(self,banco,time):
        self.cash = self.cash -self.consum_feasible
        banco.cuentas_workers[self.id].retirar(self.real_consum_feasible,time)

    def get_provider_price(self,firms):

        for firm in firms:
            if firm.id ==self.good_supplier:
                return firm.price

    def order_to_firms(self,firms,id,quantity):
        for firm in firms:
            if firm.id ==self.good_supplier:
                firm.receive_household_order(id,quantity)

    def pay_to_firms(self,firms):
        for firm in firms:
            if firm.id ==self.good_supplier:
                firm.receive_household_pay(self.consum_feasible)

    def pay_taxes(self,goverment,tax_rate):
        if self.employment== True:
            self.disposable_income = (1 - tax_rate) * self.gross_income
            goverment.tax_income+= tax_rate * self.gross_income
            self.cash-= (tax_rate * self.gross_income)

    def update_cash(self,banco):
        if self.id in banco.cuentas_workers:
            riqueza_nominal = banco.cuentas_workers[self.id].activos
            self.cash = riqueza_nominal

    def evalua_ssector(self,time):
        if self.employment_record[time]==False and self.employment_record[time-1]==False and self.employment_record[time-2]==False:
            return True
        else:
            return False

class Goverment(object):
    """docstring for Goverment."""

    def __init__(self):
        self.real_expenditure = 0
        self.real_expenditure_efective = 0
        self.nominal_expenditure = 0
        self.nominal_expenditure_efective = 0
        self.tax_profits = 0
        self.tax_income = 0
        self.balance = 0
        self.gov_supply_constraint = 0

    def set_real_expenditure(self,expenditure):
        self.real_expenditure = expenditure

    def set_nominal_expenditure(self,expenditure):
        self.nominal_expenditure = expenditure

    def define_demand_to_firms(self,firms):
        demand_by_cfirm = self.real_expenditure/len(firms)

        # El gobierno ordena su pedido a las firmas
        self.order_to_firms(firms,demand_by_cfirm)

        nominal_demand = 0

        for firm in firms:
            nominal_demand += demand_by_cfirm * firm.price

            ## El gobierno paga a las firmas
            firm.receive_goverment_pay(demand_by_cfirm * firm.price)

        self.set_nominal_expenditure(nominal_demand)

    def order_to_firms(self,firms,demand_by_cfirm):
        for firm in firms:
            firm.receive_goverment_order(demand_by_cfirm)

    def pay_consumption(self):
        self.balance = self.balance -self.nominal_expenditure

    def pay_subsidies(self, households):
        for house in households:
            if house.employment == False:
                house.disposable_income = 1

    def compute_deficit(self):
        self.balance += self.tax_profits + self.tax_income - self.nominal_expenditure_efective

class SSector(object):
    """docstring for SSector."""

    def __init__(self):
        self.workers = {}

    def incorpora_worker(self,worker):
        self.workers[worker.id]=worker

    def remueve_worker(self,worker):
        del self.workers[worker.id]

class Bank(object):
    """docstring for Bank."""

    def __init__(self,interest_rate_loans,capital):
        self.pasivos_totales = 0
        self.activos_totales = 0
        self.activos_liquidos = 20
        self.loans = 0
        self.cuentas_workers = {}
        self.cuentas_C_sector = {}
        self.cuentas_investment_C_sector = {}
        self.cuentas_K_sector = {}
        self.interest_rate_loans = {0:interest_rate_loans}
        self.retained_earnings = 0
        self.capital_adequacy_ratio ={0:0}
        self.reserve_ratio = 0
        self.capital = capital

    def compute_reserve_ratio(self):
        activos_liquidos = self.activos_liquidos
        ganancias_retenidas = self.retained_earnings

        depositos = self.compute_total_deposits()

        ratio_reserva = (activos_liquidos + ganancias_retenidas)/depositos
        print("Reserve ratio ",str(ratio_reserva))
        self.reserve_ratio = ratio_reserva

    def compute_capital_adequacy_ratio(self,time):
        capital = self.capital
        ganancias_retenidas = self.retained_earnings

        loans = self.loans

        if loans==0:
                self.capital_adequacy_ratio[time+1]=0
        else:
            self.capital_adequacy_ratio[time+1] =(capital+ganancias_retenidas)/loans

    def compute_total_deposits(self):
        depositos = 0
        for cuenta in self.cuentas_workers:
            depositos+=sum(self.cuentas_workers[cuenta].depositos.values())
        return depositos

    def compute_interest_rate_loans(self,time,target_car,target_cb):
        if self.capital_adequacy_ratio[time]<target_car:
            self.interest_rate_loans[time] = target_cb * (1 + random.uniform(0,0.05))
        else:
            self.interest_rate_loans[time] = target_cb * (1 - random.uniform(0,0.05))

class BankigAccount:
    """docstring BankigAccount"""

    def __init__(self,id,time):
        self.id = id
        self.fecha_apertura = time
        self.saldo = 0
        self.retiros = 0
        self.activos = 0
        self.pasivos = 0
        self.creditos = {}
        self.depositos = {}
        self.retiros = {}

    def depositar(self,cantidad,time):
        self.depositos[time]=cantidad
        self.activos += cantidad

    def retirar(self,cantidad,time):
        self.depositos[time]=-cantidad
        self.activos -= cantidad

class Credito:
    """docstring BankigAccount"""

    def __init__(self,time,monto,anios,interest_rate):
        self.capital = monto
        self.interest_rate = interest_rate
        self.pago = 0
        self.valor_final = 0
        self.fecha_inicio = time
        self.anios_pagar = anios
        self.deuda_total = 0

    def calcula_pago(self):
        numerador = (self.capital * self.interest_rate)
        denominador = 1 -math.pow( (1+self.interest_rate),(-1*self.anios_pagar))

        self.pago = numerador/denominador

    def calcula_vf(self):
        numerador = math.pow((1+self.interest_rate),self.anios_pagar) - 1

        self.valor_final= self.pago * (numerador/self.interest_rate)
        self.deuda_total = self.pago * self.anios_pagar

    def print_credit(self):
        print("Capital : ",str(self.capital),". Pago : ",str(self.pago),", Deuda total :",str(self.deuda_total) )



def compute_gini(households):
    agent_wealths = [agent.cash for agent in households]
    x = sorted(agent_wealths)
    N = len(agent_wealths)
    B = sum( xi * (N-i) for i,xi in enumerate(x) ) / (N*sum(x))
    return (1 + (1/N) - 2*B)
