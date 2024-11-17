"""Example for hahomematic."""

# !/usr/bin/python3
from __future__ import annotations

import asyncio
import logging
import sys
from unittest.mock import patch

from hahomematic import config, const
from hahomematic.central import CentralConfig
from hahomematic.client import InterfaceConfig, _ClientConfig
from hahomematic.model.custom import validate_custom_data_point_definition
from hahomematic_support.client_local import ClientLocal, LocalRessources

logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)

CCU_HOST = const.LOCAL_HOST
CCU_USERNAME = "xxx"
CCU_PASSWORD = "xxx"
CENTRAL_NAME = "ccu-dev"


class Example:
    """Example for hahomematic."""

    # Create a server that listens on LOCAL_HOST:* and identifies itself as myserver.
    got_devices = False

    def __init__(self):
        """Init example."""
        self.SLEEPCOUNTER = 0
        self.central = None

    def _systemcallback(self, name, *args, **kwargs):
        self.got_devices = True
        if (
            name == const.BackendSystemEvent.NEW_DEVICES
            and kwargs
            and kwargs.get("device_descriptions")
            and len(kwargs["device_descriptions"]) > 0
        ):
            self.got_devices = True
            return
        if (
            name == const.BackendSystemEvent.DEVICES_CREATED
            and kwargs
            and kwargs.get("new_data_points")
            and len(kwargs["new_data_points"]) > 0
        ):
            if len(kwargs["new_data_points"]) > 1:
                self.got_devices = True
            return

    async def example_run(self):
        """Process the example."""
        local_resources = LocalRessources(
            address_device_translation={
                "VCU3432945": "HmIP-STV.json",
                "VCU0000011": "HMW-LC-Bl1-DR.json",
                "VCU3574044": "HmIP-MOD-HO.json",
                "VCU4070501": "HmIP-FSM16.json",
                "VCU0000019": "263 155.json",
                "VCU5628817": "HmIP-SMO.json",
                "VCU0000185": "HM-RC-Sec3-B.json",
                "VCU0000079": "HM-LC-Dim1PWM-CV.json",
                "VCU0000200": "HM-RC-2-PBU-FM.json",
                "VCU0000274": "HM-Sen-MDIR-WM55.json",
                "VCU0000127": "HM-MOD-EM-8Bit.json",
                "VCU0000325": "HM-LC-Sw4-SM.json",
                "VCU0000110": "HM-LC-Dim2T-SM.json",
                "VCU0000301": "HM-LC-Sw1-Pl-DN-R3.json",
                "VCU0000172": "HM-RC-4-2.json",
                "VCU2054243": "HB-UNI-Sensor-TH-SHT75.json",
                "VCU0000103": "HM-LC-Dim1T-Pl-2.json",
                "VCU0000184": "HM-RC-Sec3.json",
                "VCU0000093": "HM-LC-Dim1T-DR.json",
                "VCU0000275": "HM-Sen-Wa-Od.json",
                "VCU5092447": "HmIP-SMO-A.json",
                "VCU3941846": "HMIP-PSM.json",
                "VCU4984404": "HmIPW-STHD.json",
                "VCU0000026": "HM-WDS20-TH-O.json",
                "VCU0000064": "HM-LC-Dim1L-Pl-2.json",
                "VCU1150287": "HmIP-HAP.json",
                "VCU0000348": "HM-Sec-WDS.json",
                "VCU0000017": "HM-PB-4Dis-WM.json",
                "VCU3560967": "HmIP-HDM1.json",
                "VCU0000287": "HM-LC-Sw2PBU-FM.json",
                "VCU0000014": "HMW-LC-Sw2-DR.json",
                "VCU0000155": "OLIGO.smart.iq.HM.json",
                "VCU0000343": "HM-Sec-TiS.json",
                "VCU5864966": "HmIP-SWDO-I.json",
                "VCU0000150": "KS550.json",
                "VCU0000121": "HM-LC-Dim1L-Pl.json",
                "VCU0000177": "HM-RC-Key4-2.json",
                "VCU0000216": "HM-Sec-RHS.json",
                "VCU0000142": "HM-Dis-TD-T.json",
                "VCU0000305": "HM-LC-Sw1-Pl-CT-R1.json",
                "VCU0000131": "HM-ES-PMSw1-Pl-DN-R3.json",
                "VCU0000114": "HM-Dis-WM55.json",
                "VCU0000105": "263 134.json",
                "VCU0000334": "HM-LC-Sw2-DR.json",
                "VCU0000328": "HM-LC-Sw1-FM.json",
                "VCU4264293": "HmIP-RCV-50.json",
                "VCU0000196": "HM-RC-12-SW.json",
                "VCU0000310": "HM-LC-Sw1-PCB.json",
                "VCU0000002": "HMW-IO-12-Sw14-DR.json",
                "VCU0000138": "HM-ES-PMSwX.json",
                "VCU4613288": "HmIP-FROLL.json",
                "VCU0000130": "HM-ES-PMSw1-Pl-DN-R2.json",
                "VCU8655720": "HmIP-CCU3.json",
                "VCU0000166": "263 135.json",
                "VCU0000339": "HM-LC-Sw1-SM-ATmega168.json",
                "VCU0000353": "WS888.json",
                "VCU0000178": "HM-RC-Key4-3.json",
                "VCU1289997": "HmIP-SPDR.json",
                "VCU0000252": "263 162.json",
                "VCU0000198": "HM-RC-19-B.json",
                "VCU0000016": "HMW-Sen-SC-12-FM.json",
                "VCU1815001": "HmIP-SWD.json",
                "VCU7171997": "HB-WDS40-THP-O.json",
                "VCU0000100": "HM-LC-Dim2T-SM-2.json",
                "VCU0000167": "HM-PB-2-FM.json",
                "VCU0000239": "ZEL STG RM FFK.json",
                "VCU2721398": "HmIPW-DRI32.json",
                "VCU0000345": "HM-WDS30-OT2-SM-2.json",
                "VCU0000025": "263 158.json",
                "VCU0000280": "HM-SwI-X.json",
                "VCU1673350": "HmIPW-FIO6.json",
                "VCU0000073": "HM-LC-Dim1L-Pl-3.json",
                "VCU5429697": "HmIP-SAM.json",
                "VCU0000096": "HM-LC-Dim2L-SM-2.json",
                "VCU0000236": "S550IA.json",
                "VCU0000211": "ZEL STG RM FDK.json",
                "VCU1530633": "HmIP-eTRV-B1.json",
                "VCU8490397": "HmIP-SWDM-B2.json",
                "VCU0000054": "HM-CC-TC.json",
                "VCU0000169": "ZEL STG RM FST UP4.json",
                "VCU4523900": "HmIP-STHO.json",
                "VCU0000340": "HM-LC-Sw4-SM-ATmega168.json",
                "VCU0000087": "HM-LC-Dim1T-Pl-3.json",
                "VCU0000137": "HM-ES-PMSw1-Pl.json",
                "VCU0000175": "HM-RC-4-3.json",
                "VCU0000341": "HM-TC-IT-WM-W-EU.json",
                "VCU0000300": "HM-LC-Sw1-Pl-DN-R2.json",
                "VCU0000081": "HM-LC-Dim1TPBU-FM-2.json",
                "VCU0000240": "HM-Sec-SC-2.json",
                "VCU8066814": "RPI-RF-MOD.json",
                "VCU4898089": "HmIP-KRC4.json",
                "VCU1954019": "HmIP-FAL230-C10.json",
                "VCU0000350": "HM-Sec-Win.json",
                "VCU0000243": "HM-SCI-3-FM.json",
                "VCU0000023": "ASH550.json",
                "VCU4567298": "HmIP-DBB.json",
                "VCU7837366": "HB-UNI-Sensor1.json",
                "VCU0000218": "WDF solar.json",
                "VCU0000327": "HM-LC-Sw4-WM.json",
                "VCU0000208": "HM-ReSC-Win-PCB-xx.json",
                "VCU0000278": "ZEL STG RM FSS UP3.json",
                "VCU0000122": "HM-LC-Dim1L-CV.json",
                "VCU0000004": "HMW-IO-12-Sw7-DR.json",
                "VCU0000055": "HM-CC-VD.json",
                "VCU0000135": "HM-ES-PMSw1-SM.json",
                "VCU0000296": "HM-LC-Sw2-FM-2.json",
                "VCU3790312": "HmIP-SWO-B.json",
                "VCU0000256": "HM-Sec-SD-Generic.json",
                "VCU0000148": "HM-Sec-Key-O.json",
                "VCU7652142": "HmIP-SRD.json",
                "VCU0000183": "HM-RC-P1.json",
                "VCU0000115": "HM-LC-DW-WM.json",
                "VCU0000322": "HM-LC-Sw1-Pl-2.json",
                "VCU0000193": "HM-RC-X.json",
                "VCU0000060": "HM-OU-CFM-TW.json",
                "VCU1891174": "HmIPW-DRS8.json",
                "VCU6874371": "HmIP-MOD-RC8.json",
                "VCU0000010": "HMW-LC-Bl1-DR-2.json",
                "VCU0000273": "HM-MD.json",
                "VCU0000018": "ZEL STG RM DWT 10.json",
                "VCU0000337": "HM-LC-SwX.json",
                "VCU0000133": "HM-ES-PMSw1-Pl-DN-R5.json",
                "VCU0000247": "HM-Sec-MDIR-2.json",
                "VCU6354483": "HmIP-STHD.json",
                "VCU0000066": "263 132.json",
                "VCU0000330": "HM-LC-Sw2-FM.json",
                "VCU1769958": "HmIP-BWTH.json",
                "VCU0000203": "BRC-H.json",
                "VCU0000304": "HM-LC-Sw1-DR.json",
                "VCU2118827": "HmIP-DLS.json",
                "VCU0000165": "ZEL STG RM WT 2.json",
                "VCU0000199": "HM-RC-19-SW.json",
                "VCU5778428": "HmIP-HEATING.json",
                "VCU0000201": "HM-RC-2-PBU-FM-2.json",
                "VCU1437294": "HmIP-SMI.json",
                "VCU0000293": "HM-LC-Sw4-PCB-2.json",
                "VCU7981740": "HmIP-SRH.json",
                "VCU0000170": "263 145.json",
                "VCU3056370": "HmIP-SLO.json",
                "VCU4243444": "HmIP-WRCD.json",
                "VCU0000036": "HM-LC-Bl1-SM-2.json",
                "VCU0000159": "HM-OU-X.json",
                "VCU0000303": "HM-LC-Sw1-Pl-DN-R5.json",
                "VCU1136001": "HB-LC-Bl1PBU-FM.json",
                "VCU1584201": "ELV-SH-BS2.json",
                "VCU0000251": "HM-Sec-MDIR.json",
                "VCU0000357": "HM-WDC7000.json",
                "VCU0000111": "HM-LC-Dim1T-FM.json",
                "VCU0000277": "HM-SwI-3-FM.json",
                "VCU0000152": "KS550Tech.json",
                "VCU0000188": "HM-PB-4-WM.json",
                "VCU1543608": "HmIP-MP3P.json",
                "VCU0000037": "HM-LC-Bl1-FM-2.json",
                "VCU0000164": "HM-PB-2-WM55.json",
                "VCU0000045": "HM-LC-Bl1-FM.json",
                "VCU0000276": "ST6-SH.json",
                "VCU2128127": "HmIP-BSM.json",
                "VCU3716619": "HmIP-BSL.json",
                "VCU6153495": "HmIP-FCI1.json",
                "VCU0000265": "HM-Sen-LI-O.json",
                "VCU0000146": "HM-Sec-Key.json",
                "VCU2737768": "HMIP-SWDO.json",
                "VCU0000143": "HM-WDS100-C6-O-2.json",
                "VCU0000302": "HM-LC-Sw1-Pl-DN-R4.json",
                "VCU0000057": "HM-RCV-50.json",
                "VCU1152627": "HmIP-RC8.json",
                "VCU0000336": "ZEL STG RM FZS-2.json",
                "VCU0000279": "263 144.json",
                "VCU0000012": "HMW-LC-Dim1L-DR.json",
                "VCU0000094": "HM-LC-Dim1T-FM-LF.json",
                "VCU0000292": "HM-LC-Sw4-SM-2.json",
                "VCU7204276": "HmIP-DRSI4.json",
                "VCU2333555": "HmIP-FSI16.json",
                "VCU5424977": "HmIP-DSD-PCB.json",
                "VCU8063453": "HmIP-STH.json",
                "VCU0000237": "HM-WDS30-T-O.json",
                "VCU0000332": "HM-LC-Sw2-PB-FM.json",
                "VCU0000021": "HM-LC-AO-SM.json",
                "VCU0000264": "HM-Sen-X.json",
                "VCU0000132": "HM-ES-PMSw1-Pl-DN-R4.json",
                "VCU0000246": "HM-Sec-MDIR-3.json",
                "VCU0000145": "HM-LC-JaX.json",
                "VCU0000083": "263 133.json",
                "VCU0000346": "HM-WDS40-TH-I-2.json",
                "VCU0000182": "HM-RC-4-B.json",
                "VCU0000190": "RC-H.json",
                "VCU8775962": "HmIP-PCBS2.json",
                "VCU9344471": "HmIP-SPI.json",
                "VCU6167284": "HB-UNI-Sen-PRESS.json",
                "VCU0000351": "HM-Sec-Win-Generic.json",
                "VCU0000015": "HMW-Sen-SC-12-DR.json",
                "VCU7935803": "HMIP-WRC2.json",
                "VCU0000289": "HM-LC-Sw1-Pl-3.json",
                "VCU2680226": "HmIP-WTH-2.json",
                "VCU6306084": "HmIP-BRC2.json",
                "VCU0000335": "ZEL STG RM FZS.json",
                "VCU7994929": "HB-LC-Sw1PBU-FM.json",
                "VCU0000168": "HM-PBI-4-FM.json",
                "VCU0000074": "HM-LC-Dim1L-CV-2.json",
                "VCU0000288": "HM-LC-Sw4-Ba-PCB.json",
                "VCU2573721": "HmIP-SMO-2.json",
                "VCU0000180": "HM-RC-Sec4-3.json",
                "VCU0000181": "HM-RC-4.json",
                "VCU0000186": "HM-RC-Key3.json",
                "VCU0000272": "HM-Sen-MDIR-O.json",
                "VCU0000329": "263 130.json",
                "VCU0000309": "HM-LC-Sw1-Pl-CT-R5.json",
                "VCU9341719": "HmIP-PCBS-BAT.json",
                "INT0000001": "HM-CC-VG-1.json",
                "VCU0000354": "WS550Tech.json",
                "VCU0000259": "263 167.json",
                "VCU0000344": "HM-WDS30-OT2-SM.json",
                "VCU8249617": "HmIP-ASIR-2.json",
                "VCU0000158": "HM-OU-LED16.json",
                "VCU1371379": "HmIP-WTH-1.json",
                "VCU1004487": "HmIPW-DRAP.json",
                "VCU0000290": "HM-LC-Sw1-SM-2.json",
                "VCU7549831": "HmIP-STE2-PCB.json",
                "VCU0000082": "HM-LC-Dim1TPBU-FM.json",
                "VCU0000321": "HM-LC-Sw1-Pl.json",
                "VCU0000206": "HM-Sen-RD-O.json",
                "VCU7755574": "ALPHA-IP-RBG.json",
                "VCU9724704": "HmIP-DLD.json",
                "VCU1768323": "HmIP-eTRV-C-2.json",
                "VCU0000217": "HM-Sec-xx.json",
                "VCU0000123": "HM-LC-Dim2L-CV.json",
                "VCU0000295": "HM-LC-Sw1-FM-2.json",
                "VCU0000056": "ZEL STG RM FSA.json",
                "VCU0000078": "HM-LC-Dim1PWM-CV-2.json",
                "VCU0000001": "HMW-RCV-50.json",
                "VCU1795819": "HB-LC-Sw2PBU-FM.json",
                "VCU0000051": "HM-CC-RT-DN-BoM.json",
                "VCU0000153": "KS550LC.json",
                "VCU0000174": "HM-RC-8.json",
                "VCU0000192": "ZEL STG RM HS 4.json",
                "VCU0000171": "HM-PBI-X.json",
                "VCU0000027": "HM-WDS40-TH-I.json",
                "VCU0000088": "HM-LC-Dim1T-CV-2.json",
                "VCU0000043": "263 147.json",
                "VCU8205532": "HmIP-SCTH230.json",
                "VCU0000266": "HM-Sen-MDIR-O-3.json",
                "VCU0000352": "WS550.json",
                "VCU0000331": "HM-LC-Sw1-PB-FM.json",
                "VCU3880755": "HB-UNI-Sensor-THPD-BME280.json",
                "VCU0000020": "HM-PB-4Dis-WM-2.json",
                "VCU0000267": "HM-Sen-MDIR-O-2.json",
                "VCU3830359": "HmIP-PCBS.json",
                "VCU1841406": "HmIP-SWO-PL.json",
                "VCU2826390": "HmIPW-STH.json",
                "VCU0000197": "HM-RC-19.json",
                "VCU0000260": "HM-Sec-SFA-SM.json",
                "VCU0000007": "HMW-IO-4-FM.json",
                "VCU3188750": "HmIP-WGC.json",
                "VCU0000048": "263 146.json",
                "VCU6177550": "HmIP-eTRV-2 I9F.json",
                "VCU0000062": "CMM.json",
                "VCU3609622": "HmIP-eTRV-2.json",
                "VCU4743739": "HmIPW-SPI.json",
                "VCU0000294": "HM-LC-Sw4-WM-2.json",
                "VCU0000187": "HM-RC-Key3-B.json",
                "VCU6948166": "HmIP-DRDI3.json",
                "VCU0000311": "HM-MOD-Re-8.json",
                "VCU0000202": "HM-RC-Dis-H-x-EU.json",
                "VCU5801873": "HmIP-PMFS.json",
                "VCU3747418": "HM-LC-RGBW-WM.json",
                "VCU0000324": "HM-LC-Sw2-SM.json",
                "VCU5644414": "HmIP-SWDM.json",
                "VCU0000262": "HM-Sen-DB-PCB.json",
                "VCU8539034": "HmIP-WRCR.json",
                "VCU0000022": "ASH550I.json",
                "VCU0000126": "HM-MOD-EM-8.json",
                "VCU0000149": "HM-Sec-Key-Generic.json",
                "VCU0000151": "KS888.json",
                "VCU0000059": "HM-OU-CFM-Pl.json",
                "VCU0000254": "HM-Sec-SCo.json",
                "VCU3015080": "HmIP-SCI.json",
                "VCU0000125": "HSS-DX.json",
                "VCU0000049": "HM-LC-BlX.json",
                "VCU0000333": "HM-LC-Sw4-DR.json",
                "VCU0000047": "ZEL STG RM FEP 230V.json",
                "VCU0000312": "HM-LC-Sw1-Ba-PCB.json",
                "VCU1494703": "HmIP-eTRV-E.json",
                "VCU0000070": "HM-LC-DDC1-PCB.json",
                "VCU0000053": "ZEL STG RM FWT.json",
                "VCU0000005": "HMW-IO-12-FM.json",
                "VCU9333179": "HmIP-ASIR.json",
                "VCU0000046": "HM-LC-Bl1-PB-FM.json",
                "VCU0000204": "HM-RC-SB-X.json",
                "VCU0000207": "HM-Sys-sRP-Pl.json",
                "VCU0000286": "263 131.json",
                "VCU0000308": "HM-LC-Sw1-Pl-CT-R4.json",
                "VCU8126977": "HmIP-MOD-OC8.json",
                "VCU4704397": "HmIPW-WRC6.json",
                "VCU7807849": "HmIPW-DRBL4.json",
                "VCU0000255": "HM-Sec-SD.json",
                "VCU5597068": "HmIPW-SMI55.json",
                "VCU0000179": "HM-RC-Sec4-2.json",
                "VCU1399816": "HmIP-BDT.json",
                "VCU0000044": "HM-LC-Bl1-SM.json",
                "VCU6166407": "HmIP-MOD-TM.json",
                "VCU0000297": "HM-LC-Sw4-DR-2.json",
                "VCU0000191": "atent.json",
                "VCU0000089": "HM-LC-Dim1T-FM-2.json",
                "VCU0000029": "IS-WDS-TH-OD-S-R3.json",
                "VCU8255833": "HmIP-STHO-A.json",
                "VCU1803301": "HmIP-USBSM.json",
                "VCU9933791": "HmIPW-DRD3.json",
                "VCU0000299": "HM-LC-Sw1-Pl-DN-R1.json",
                "VCU1366171": "HMIP-PS.json",
                "VCU6977344": "HmIP-MIO16-PCB.json",
                "VCU0000212": "HM-Sec-RHS-2.json",
                "VCU0000028": "263 157.json",
                "VCU0000108": "HM-LC-Dim1T-Pl.json",
                "VCU2913614": "HmIP-WHS2.json",
                "VCU8585352": "HmIP-DRSI1.json",
                "VCU8451105": "HmIPW-WTH.json",
                "VCU1362746": "HmIP-SWO-PR.json",
                "VCU7631078": "HmIP-FDT.json",
                "VCU0000154": "HM-WDS100-C6-O.json",
                "VCU0000356": "WS550LCW.json",
                "VCU0000124": "HM-LC-Dim2L-SM.json",
                "VCU0000253": "HM-Sec-MD.json",
                "VCU0000113": "HM-Dis-EP-WM55.json",
                "VCU0000245": "HM-Sec-SC.json",
                "VCU1223813": "HmIP-FBL.json",
                "VCU0000307": "HM-LC-Sw1-Pl-CT-R3.json",
                "VCU0000129": "HM-ES-PMSw1-Pl-DN-R1.json",
                "VCU8688276": "HmIP-eTRV-B.json",
                "VCU0000241": "HM-CC-SCD.json",
                "VCU6531931": "HmIP-RCB1.json",
                "VCU0000008": "HMW-IO-SR-FM.json",
                "VCU0000194": "HM-RC-12.json",
                "VCU0000144": "HM-LC-Ja1PBU-FM.json",
                "VCU0000355": "WS550LCB.json",
                "VCU0000042": "HM-LC-Bl1PBU-FM.json",
                "VCU2304696": "HB-UNI-Sen-TEMP-DS18B20.json",
                "VCU0000061": "HM-OU-CM-PCB.json",
                "VCU1111390": "HmIP-HDM2.json",
                "VCU0000258": "HM-Sec-SD-2-Generic.json",
                "VCU0000050": "HM-CC-RT-DN.json",
                "VCU0000141": "HM-ES-TX-WM.json",
                "VCU0000109": "HM-LC-Dim1T-CV.json",
                "VCU2822385": "HmIP-SWSD.json",
                "VCU0000160": "HM-PB-2-WM55-2.json",
                "VCU1533290": "HmIP-WRC6.json",
                "VCU5334484": "HmIP-KRCA.json",
                "VCU1260322": "HmIP-RFUSB.json",
                "VCU0000242": "263 160.json",
                "VCU0000306": "HM-LC-Sw1-Pl-CT-R2.json",
                "VCU0000298": "HM-LC-Sw2-DR-2.json",
                "VCU0000338": "HM-LC-Sw1-Pl-OM54.json",
                "VCU0000195": "HM-RC-12-B.json",
                "VCU0000176": "HM-RC-4-3-D.json",
                "VCU0000261": "HM-Sec-Sir-WM.json",
                "VCU8537918": "HmIP-BROLL.json",
                "VCU0000134": "HM-ES-PMSw1-DR.json",
                "VCU0000326": "HM-LC-Sw4-PCB.json",
                "VCU0000271": "HM-Sen-MDIR-SM.json",
                "VCU9981826": "HmIP-SFD.json",
                "VCU0000349": "HM-Sec-WDS-2.json",
                "VCU9973336": "HBW-LC-RGBWW-IN6-DR.json",
                "VCU0000189": "HM-PB-2-WM.json",
                "VCU0000098": "HM-DW-WM.json",
                "VCU0000058": "HM-OU-CF-Pl.json",
                "VCU0000285": "HM-LC-Sw1PBU-FM.json",
                "VCU0000257": "HM-Sec-SD-2.json",
                "VCU0000147": "HM-Sec-Key-S.json",
                "VCU2428569": "HmIPW-FAL230-C6.json",
                "VCU0000263": "HM-Sen-EP.json",
                "VCU9628024": "HmIPW-FALMOT-C12.json",
                "VCU0000024": "HM-WDS10-TH-O.json",
                "VCU0000173": "HM-PB-6-WM55.json",
                "VCU9710932": "HmIP-SMI55.json",
                "VCU0000323": "HM-LC-Sw1-SM.json",
            },
            ignore_devices_on_create=[],
        )

        interface_config = InterfaceConfig(
            central_name=CENTRAL_NAME,
            interface=const.Interface.BIDCOS_RF,
            port=2002,
        )

        self.central = CentralConfig(
            name=CENTRAL_NAME,
            host=CCU_HOST,
            username=CCU_USERNAME,
            password=CCU_PASSWORD,
            central_id="1234",
            storage_folder="homematicip_local",
            interface_configs={interface_config},
            client_session=None,
            default_callback_port=48888,
        ).create_central()

        # Add callbacks to handle the events and see what happens on the system.
        self.central.register_backend_system_callback(self._systemcallback)

        client = ClientLocal(
            client_config=_ClientConfig(
                central=self.central,
                interface_config=interface_config,
            ),
            local_resources=local_resources,
        )
        await client.init_client()

        # For testing we set a short INIT_TIMEOUT
        config.INIT_TIMEOUT = 10

        with (
            patch("hahomematic.central.CentralUnit._get_primary_client", return_value=client),
            patch("hahomematic.client._ClientConfig.get_client", return_value=client),
        ):
            await self.central.start()
            await self.central._refresh_device_descriptions(client=client)

        while not self.got_devices and self.SLEEPCOUNTER < 20:
            _LOGGER.info("Waiting for devices")
            self.SLEEPCOUNTER += 1
            await asyncio.sleep(1)
        await asyncio.sleep(5)

        for i in range(16):
            _LOGGER.info("Sleeping (%i)", i)
            await asyncio.sleep(2)
        # Stop the central_1 thread so Python can exit properly.
        await self.central.stop()


# validate the device description
if validate_custom_data_point_definition():
    example = Example()
    asyncio.run(example.example_run())
    sys.exit(0)
