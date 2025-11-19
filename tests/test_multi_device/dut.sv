module dut
#(
    integer G_REGWIDTH = 32,
    integer G_ADDR_WIDTH = 7,
    integer G_NUM_SLAVES = 8
)
(
    input wire clk,
    input wire rst,

    // APB Slave Interface (Driven by testbench Master)
    input wire [G_NUM_SLAVES-1:0] s_apb_psel,
    input wire s_apb_penable,
    input wire s_apb_pwrite,
    input wire [2:0] s_apb_pprot,
    input wire [G_ADDR_WIDTH-1:0] s_apb_paddr,
    input wire [G_REGWIDTH-1:0] s_apb_pwdata,
    input wire [(G_REGWIDTH/8)-1:0] s_apb_pstrb,
    output logic [(G_NUM_SLAVES*1)-1:0] s_apb_pready,
    output logic [(G_NUM_SLAVES*G_REGWIDTH)-1:0] s_apb_prdata,
    output logic [(G_NUM_SLAVES*1)-1:0] s_apb_pslverr
);

for (genvar i = 0; i < G_NUM_SLAVES; i++) begin : gen_slaves
    regblock i_regblock (
        .*
        ,.s_apb_psel(s_apb_psel[i])
        ,.s_apb_prdata(s_apb_prdata[i*G_REGWIDTH +: G_REGWIDTH])
        ,.s_apb_pslverr(s_apb_pslverr[i])
        ,.s_apb_pready(s_apb_pready[i])
    );
end

endmodule
