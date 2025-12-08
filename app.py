// src/components/ScheduleResult.tsx
import { RouteData } from "@/types/route";
import { Truck, MapPin, Clock, User } from "lucide-react";

interface ScheduleResultProps {
  route: RouteData;
}

export const ScheduleResult = ({ route }: ScheduleResultProps) => {
  return (
    <div className="bg-card text-card-foreground rounded-lg p-6 shadow-sm border border-border animate-fade-in">
      {/* Cabeçalho: Motorista e VPN */}
      <div className="flex justify-between items-start mb-4 border-b border-border pb-4">
        <div>
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <User className="w-5 h-5 text-primary" />
            {route.motorista}
          </h3>
          <span className="text-sm text-muted-foreground ml-7 font-mono">
            VPN: {route.vpn}
          </span>
        </div>
        <div className="flex items-center gap-1 text-primary font-mono font-bold bg-primary/10 px-3 py-1 rounded">
           <Truck className="w-4 h-4" />
           {route.matricula}
        </div>
      </div>

      {/* Detalhes da Rota */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Localização */}
        <div className="space-y-2">
            <div className="flex items-start gap-3">
                <MapPin className="w-5 h-5 text-muted-foreground mt-1" />
                <div>
                    <p className="font-medium text-lg">{route.local}</p>
                    <div className="flex gap-3 text-sm text-muted-foreground mt-1">
                        <span className="bg-secondary px-2 py-0.5 rounded text-secondary-foreground">
                          Rota: {route.rota}
                        </span>
                        <span className="bg-secondary px-2 py-0.5 rounded text-secondary-foreground">
                          Loja: {route.nLoja}
                        </span>
                    </div>
                </div>
            </div>
        </div>

        {/* Horários */}
        <div className="space-y-3 bg-muted/30 p-3 rounded-md border border-border/50">
             <div className="flex items-center gap-3">
                <Clock className="w-5 h-5 text-muted-foreground" />
                <div className="text-sm w-full space-y-1">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Chegada Azambuja:</span> 
                      <span className="font-mono font-medium">{route.horaChegada}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Descarga Loja:</span> 
                      <span className="font-mono font-bold text-primary">{route.horaDescarga}</span>
                    </div>
                </div>
            </div>
        </div>

      </div>
    </div>
  );
};
