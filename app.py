// src/components/ScheduleResult.tsx
import { RouteData } from "@/types/route";
import { Truck, MapPin, Clock, User, Hash } from "lucide-react";

interface ScheduleResultProps {
  route: RouteData;
}

export const ScheduleResult = ({ route }: ScheduleResultProps) => {
  return (
    <div className="bg-card text-card-foreground rounded-lg p-6 shadow-sm border border-border animate-fade-in">
      
      {/* Cabeçalho do Card: Motorista e VPN */}
      <div className="flex justify-between items-start mb-4 border-b border-border pb-4">
        <div>
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <User className="w-5 h-5 text-primary" />
            {route.motorista}
          </h3>
          <span className="text-sm text-muted-foreground ml-7">VPN: {route.vpn}</span>
        </div>
        <div className="text-right">
             <div className="flex items-center gap-1 text-primary font-mono font-bold bg-primary/10 px-2 py-1 rounded">
                <Truck className="w-4 h-4" />
                {route.matricula}
             </div>
        </div>
      </div>

      {/* Detalhes da Rota */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        
        {/* Localização */}
        <div className="space-y-3">
            <div className="flex items-start gap-3">
                <MapPin className="w-5 h-5 text-muted-foreground mt-0.5" />
                <div>
                    <p className="font-medium">{route.local}</p>
                    <p className="text-xs text-muted-foreground">Rota: {route.rota} | Loja/Cais: {route.nLoja}</p>
                </div>
            </div>
        </div>

        {/* Horários */}
        <div className="space-y-3">
             <div className="flex items-center gap-3">
                <Clock className="w-5 h-5 text-muted-foreground" />
                <div className="text-sm">
                    <p><span className="text-muted-foreground">Chegada Azambuja:</span> <span className="font-mono">{route.horaChegada}</span></p>
                    <p><span className="text-muted-foreground">Descarga Loja:</span> <span className="font-mono font-semibold">{route.horaDescarga}</span></p>
                </div>
            </div>
        </div>

      </div>
    </div>
  );
};
