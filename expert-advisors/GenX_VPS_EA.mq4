//+------------------------------------------------------------------+
//|                                                   GenX_VPS_EA.mq4 |
//|                                    GenX FX Trading System VPS EA |
//|                                   Optimized for VPS + AWS Signals |
//+------------------------------------------------------------------+
#property copyright "GenX FX"
#property version   "1.00"
#property strict

// Input Parameters
input double LotSize = 0.01;
input int MagicNumber = 12345;
input string SignalURL = "http://YOUR_AWS_IP:8000/MT4_Signals.csv";
input int SignalCheckInterval = 300; // 5 minutes
input double MaxRisk = 2.0; // Max risk per trade %

// Global Variables
datetime lastSignalCheck = 0;
string signalData = "";

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit() {
    Print("GenX VPS EA Started - Connecting to AWS Signals");
    
    // Enable WebRequest for the signal URL
    if(!TerminalInfoInteger(TERMINAL_DLLS_ALLOWED)) {
        Alert("Please enable DLL imports in EA settings");
        return INIT_FAILED;
    }
    
    return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick() {
    // Check for new signals every 5 minutes
    if(TimeCurrent() - lastSignalCheck >= SignalCheckInterval) {
        CheckForNewSignals();
        lastSignalCheck = TimeCurrent();
    }
}

//+------------------------------------------------------------------+
//| Download and process signals from AWS                           |
//+------------------------------------------------------------------+
void CheckForNewSignals() {
    string filename = "genx_signals.csv";
    string url = SignalURL;
    
    // Download signals
    char data[];
    char headers[];
    string result_headers;
    int timeout = 5000;
    
    int res = WebRequest("GET", url, "", "", timeout, data, ArraySize(data), result_headers);
    
    if(res == 200) {
        signalData = CharArrayToString(data);
        ProcessSignals(signalData);
        Print("Signals updated from AWS");
    } else {
        Print("Failed to download signals. Error: ", res);
    }
}

//+------------------------------------------------------------------+
//| Process CSV signals and execute trades                          |
//+------------------------------------------------------------------+
void ProcessSignals(string csvData) {
    string lines[];
    int lineCount = StringSplit(csvData, '\n', lines);
    
    for(int i = 1; i < lineCount; i++) { // Skip header
        string fields[];
        int fieldCount = StringSplit(lines[i], ',', fields);
        
        if(fieldCount >= 6) {
            string symbol = fields[0];
            string action = fields[1];
            double entry = StringToDouble(fields[2]);
            double sl = StringToDouble(fields[3]);
            double tp = StringToDouble(fields[4]);
            double confidence = StringToDouble(fields[5]);
            
            // Only trade current symbol with high confidence
            if(symbol == Symbol() && confidence >= 0.7) {
                ExecuteSignal(action, entry, sl, tp, confidence);
            }
        }
    }
}

//+------------------------------------------------------------------+
//| Execute trading signal                                           |
//+------------------------------------------------------------------+
void ExecuteSignal(string action, double entry, double sl, double tp, double confidence) {
    // Check if we already have a position
    if(PositionsTotal() > 0) return;
    
    // Calculate lot size based on confidence and risk
    double lots = CalculateLotSize(sl, confidence);
    
    int orderType = -1;
    if(action == "BUY") orderType = OP_BUY;
    else if(action == "SELL") orderType = OP_SELL;
    
    if(orderType != -1) {
        double price = (orderType == OP_BUY) ? Ask : Bid;
        
        int ticket = OrderSend(Symbol(), orderType, lots, price, 3, sl, tp, 
                              "GenX VPS EA", MagicNumber, 0, clrGreen);
        
        if(ticket > 0) {
            Print("Order executed: ", action, " ", lots, " lots at ", price);
        } else {
            Print("Order failed. Error: ", GetLastError());
        }
    }
}

//+------------------------------------------------------------------+
//| Calculate lot size based on risk and confidence                 |
//+------------------------------------------------------------------+
double CalculateLotSize(double stopLoss, double confidence) {
    double balance = AccountBalance();
    double riskAmount = balance * (MaxRisk / 100.0);
    
    // Adjust risk based on confidence
    riskAmount = riskAmount * confidence;
    
    double pipValue = MarketInfo(Symbol(), MODE_TICKVALUE);
    double stopLossPips = MathAbs(Ask - stopLoss) / Point;
    
    double lots = riskAmount / (stopLossPips * pipValue);
    
    // Normalize lot size
    double minLot = MarketInfo(Symbol(), MODE_MINLOT);
    double maxLot = MarketInfo(Symbol(), MODE_MAXLOT);
    double lotStep = MarketInfo(Symbol(), MODE_LOTSTEP);
    
    lots = MathMax(minLot, MathMin(maxLot, lots));
    lots = NormalizeDouble(lots / lotStep, 0) * lotStep;
    
    return lots;
}

//+------------------------------------------------------------------+
//| Get total positions                                              |
//+------------------------------------------------------------------+
int PositionsTotal() {
    int count = 0;
    for(int i = 0; i < OrdersTotal(); i++) {
        if(OrderSelect(i, SELECT_BY_POS) && 
           OrderSymbol() == Symbol() && 
           OrderMagicNumber() == MagicNumber) {
            count++;
        }
    }
    return count;
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                |
//+------------------------------------------------------------------+
void OnDeinit(const int reason) {
    Print("GenX VPS EA Stopped");
}