module dut
#(
      integer REGWIDTH = 64
      , integer N_REGS = 32
      , integer G_ADDR_WIDTH = $clog2(N_REGS)+$clog2(REGWIDTH/8)
)
(
        input wire clk,
        input wire rst,

        input wire s_apb_psel,
        input wire s_apb_penable,
        input wire s_apb_pwrite,
        input wire [2:0] s_apb_pprot,
        input wire [G_ADDR_WIDTH-1:0] s_apb_paddr,
        input wire [REGWIDTH-1:0] s_apb_pwdata,
        input wire [(REGWIDTH/8)-1:0] s_apb_pstrb,
        output logic s_apb_pready,
        output logic [REGWIDTH-1:0] s_apb_prdata,
        output logic s_apb_pslverr
);



    top i_top (
        .*
    );


endmodule
