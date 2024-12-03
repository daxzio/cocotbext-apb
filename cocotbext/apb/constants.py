import enum


# Protection bits
# PPROT
class ApbProt(enum.IntFlag):
    PRIVILEGED = 0b001
    NONSECURE = 0b010
    INSTRUCTION = 0b100


# from typing import NamedTuple
# from cocotb.triggers import Event
# class ApbWriteCmd(NamedTuple):
#     address: int
#     data: bytes
#     prot: ApbProt
#     event: Event
#
#
# class ApbReadCmd(NamedTuple):
#     address: int
#     prot: ApbProt
#     event: Event
