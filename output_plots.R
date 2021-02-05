### Limpiamos el área de trabajo
rm(list=ls())

### Cargamos bibliotecas
library(ggplot2)
library(Rmisc)
library(reshape2)

### Cargamos la lista de csv
tablas<-read.table(paste(getwd(),"/data/","resultados_csv.txt",sep=""),col.names = "salidas")
tablas<-as.vector(tablas$salidas)

titulos<-c("Balance de Gobierno","Capital","Cash bill","Consumo Real Efectivo","Demanda de Gobierno","Ganancias","Coeficiente de Gini","Precios promedio normalizados","Porcentaje de población ocupada en el Sector de Subsistencia","Precios Promedio de Bienes de Consumo","Producto del Sector de Bienes de Consumo","Producto del Sector de Bienes de Capital","Salarios","Participación de las Ganancias en el Ingreso","Participación de los Salarios en el Ingreso","Tasa de desempleo")

for (i in c(1:length(tablas))) {
  df<-read.csv(paste(getwd(),"/data/",tablas[i],sep=""))
  df_melt <- melt(df, id=c("sim","alpha"))
  df_melt$variable<-gsub("X","",df_melt$variable)
  colnames(df_melt)<-c("sim","alpha","periodo","value")
  datos_sum<-summarySE(df_melt, measurevar="value",groupvars = c("periodo","alpha"))
  datos_sum$periodo<-as.numeric(as.character(datos_sum$periodo))
  attach(datos_sum)

  datos_sum <- datos_sum[order(periodo),]

  detach(datos_sum)

  pd <- position_dodge(0.1)
  p<-ggplot(datos_sum, aes(x=periodo, y=value,colour = alpha)) +
    geom_errorbar(aes(ymin=value-se, ymax=value+se,group = alpha), colour="gray", width=0.5, position=pd) +
    geom_line(position=pd,aes(group = alpha)) +
    geom_point(position=pd, size=1, shape=21, aes(group = alpha,fill=alpha)) + # 21 is filled circle
    labs(x="Periodos",
         y="",
         title=titulos[i],
         subtitle="Simulaciones = 50")+
    theme_bw()
  print(paste("Tabla ",tablas[i]))
  ggsave(p, file=paste(getwd(),"/images/",gsub(".csv","",tablas[i]),".eps",sep=""), device="eps")

}
