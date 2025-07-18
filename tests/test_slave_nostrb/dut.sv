module dut
#(
        integer G_REGWIDTH = 32
      , integer G_ADDR_WIDTH = 32
)
(
        input wire clk,
        input wire rst,

        output wire m_apb_psel,
        output wire m_apb_penable,
        output wire m_apb_pwrite,
        output wire [2:0] m_apb_pprot,
        output wire [G_ADDR_WIDTH-1:0] m_apb_paddr,
        output wire [G_REGWIDTH-1:0] m_apb_pwdata,
        input logic m_apb_pready,
        input logic [G_REGWIDTH-1:0] m_apb_prdata,
        input logic m_apb_pslverr,

        input wire s_apb_psel,
        input wire s_apb_penable,
        input wire s_apb_pwrite,
        input wire [2:0] s_apb_pprot,
        input wire [G_ADDR_WIDTH-1:0] s_apb_paddr,
        input wire [G_REGWIDTH-1:0] s_apb_pwdata,
        output logic s_apb_pready,
        output logic [G_REGWIDTH-1:0] s_apb_prdata,
        output logic s_apb_pslverr
);

assign m_apb_psel     = s_apb_psel;
assign m_apb_penable  = s_apb_penable;
assign m_apb_pwrite   = s_apb_pwrite;
assign m_apb_pprot    = s_apb_pprot;
assign m_apb_paddr    = s_apb_paddr;
assign m_apb_pwdata   = s_apb_pwdata;

assign s_apb_pready   = m_apb_pready;
assign s_apb_prdata   = m_apb_prdata;
assign s_apb_pslverr  = m_apb_pslverr;


endmodule
