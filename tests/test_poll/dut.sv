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
    input wire s_apb_psel,
    input wire s_apb_penable,
    input wire s_apb_pwrite,
    input wire [2:0] s_apb_pprot,
    input wire [G_ADDR_WIDTH-1:0] s_apb_paddr,
    input wire [G_REGWIDTH-1:0] s_apb_pwdata,
    input wire [(G_REGWIDTH/8)-1:0] s_apb_pstrb,
    output logic s_apb_pready,
    output logic [G_REGWIDTH-1:0] s_apb_prdata,
    output logic s_apb_pslverr
);

logic w_start;
logic f_busy;
logic d_busy;
logic [3:0] f_cnt;
logic [3:0] d_cnt;


    regblock i_regblock (
        .*
        ,.hwif_out_start(w_start)
        ,.hwif_in_busy(f_busy)
    );

    always @(*) begin : p_sm
        d_busy = f_busy;
        d_cnt = f_cnt;
        if (0 == f_cnt) d_busy = 0;
        if (w_start) begin
            d_busy = 1;
            d_cnt = 15;
        end
        if (f_busy) d_cnt = f_cnt - 1;
    end

    always @(posedge clk) begin : p_reg
        if (rst) begin
            f_busy <= 0;
            f_cnt <= 0;
        end else begin
            f_busy <= d_busy;
            f_cnt <= d_cnt;
        end
    end



endmodule
