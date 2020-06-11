import discord
from discord.ext import commands, tasks

from configparser import ConfigParser
config = ConfigParser()
config.read("config.ini")
server_id = int(config.get("GENERAL", "server_id"))
embed_colour = discord.Color.blue()

from EUCLib import ReactionsTracker as RTracker

class reactionsAdd(commands.Cog):
    
    def __init__(self, client):
        self.client = client
        self.num_react = {
            1: "1\N{combining enclosing keycap}",
            2: "2\N{combining enclosing keycap}",
            3: "3\N{combining enclosing keycap}",
            4: "4\N{combining enclosing keycap}",
            5: "5\N{combining enclosing keycap}",
            6: "6\N{combining enclosing keycap}",
            7: "7\N{combining enclosing keycap}",
            8: "8\N{combining enclosing keycap}",
            9: "9\N{combining enclosing keycap}",
            10: "10\N{combining enclosing keycap}"
        }
        self.letter_react = {
            "\U0001f1fc": "W",
            "\U0001f1ee": "I",
            "\U0001f1f2": "M",
            "\U0001f1f8": "S",
            "\U0001f1ea": "E",
            "\U0001f1f3": "N",
            "\U0001f534": "CANCEL"
        }
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        guild = self.client.get_guild(int(config.get('GENERAL', 'server_id')))
        r_user_id = payload.user_id
        r_message_id = payload.message_id
        r_channel_id = payload.channel_id
        if not r_user_id == self.client.user.id:
            msg_source = payload.guild_id
            if not msg_source:
                msg_source = 0
            res, m_type, m_info = RTracker().fetchMessage(r_message_id)
            if not msg_source == 0:
                if m_type == "RANK":
                    m_info = m_info.split(" ")
                    m_state = m_info[0]
                    m_target_user = m_info[1]
                    if m_state == "CH1":
                        print("a")
                
                if m_type == "SF":
                    m_info = m_info.split(" ")
                    m_state = m_info[0]
                    m_target_user = m_info[1]
                    m_target_channel = m_info[2]
                    if m_state == "CH1":
                        target_channel = self.client.get_channel(int(m_target_channel))
                        target_message = await target_channel.fetch_message(int(r_message_id))
                        if payload.emoji.name in self.letter_react:
                            if self.letter_react[payload.emoji.name] == "CANCEL":
                                await target_message.delete()
                                old_l = []
                                old_l.append(r_message_id)
                                RTracker().retireMessages(old_l)
                                return
                            
                            sf_embed_data = {
                                "W": {
                                    "title": "EURW sector files",
                                    "value1": "- **EURW sector file repository:** [click here](http://files.aero-nav.com/EURO)\n- **EURW VOR & NDB list:** [click here](https://vacc-euc.org/files/VORNDB_EURW.pdf)",
                                    "value2": "- **Frequency:** `135.250`\n- **FIRs covered:** France (Bordeaux/LFBB, Reims/LFEE, Marseille/LFMM, Brest/LFRR, Paris/LFFF), Portugal (Lisboa/LPPC), Spain (Madrid/LECM, Barcelona/LECB)",
                                    "image": "https://vacc-euc.org/img/EURW.png"
                                },
                                "I": {
                                    "title": "EURI sector files",
                                    "value1": "- **EURI sector file repository:** [click here](http://files.aero-nav.com/EURO)\n- **EURI VOR & NDB list:** [click here](https://vacc-euc.org/files/VORNDB_EURI.pdf)",
                                    "value2": "- **Frequency:** `135.750`\n- **FIRs covered:** Iceland (Reykjavik/BIRD), Ireland (Shannon/EISN), United Kingdom (London/EGTT, Scottish/EGPX)",
                                    "image": "https://vacc-euc.org/img/EURI.jpg"
                                },
                                "N": {
                                    "title": "EURN sector files",
                                    "value1": "- **EURN sector file repository:** [click here](http://files.aero-nav.com/EURO)\n- **EURN VOR & NDB list:** [click here](https://vacc-euc.org/files/VORNDB_EURN.pdf)",
                                    "value2": "- **Frequency:** `133.450`\n- **FIRs covered:** Denmark (Copenhagen/EKDK), Estonia (Tallinn/EETT), Finland (Helsinki/EFIN), Latvia (Riga/EVRR), Lithuania (Vilnius/EYVL), Norway (ENOR now covering Bodø/ENBD, former Trondheim/ENTR, Stavanger/ENSV, Oslo/ENOS), Sweden (Sweden/ESAA)",
                                    "image": "https://vacc-euc.org/img/EURN.png"
                                },
                                "E": {
                                    "title": "EURE sector files",
                                    "value1": "- **EURE sector file repository:** [click here](http://files.aero-nav.com/EURO)\n- **EURE VOR & NDB list:** [click here](https://vacc-euc.org/files/VORNDB_EURE.pdf)",
                                    "value2": "- **Frequency:** `135.300`\n- **FIRs covered:** Albania (Tirana/LAAA), Bosnia-Herzegovina (Sarajevo/LQSB), Bulgaria (Sofia/LBSR, Varna/LBWR), Croatia (Zagreb/LDZO), Czech Republic (Praha/LKAA), FYRoM (Skopje/LWSS), Hungary (Budapest/LHCC), Moldova (Chisinau/LUKK), Poland (Warszawa/EPWW), Romania (Bucaresti/LRBB), Serbia & Montenegro (Beograd/LYBA), Slovakia (Bratislava/LZBB), Slovenia (Ljubljana/LJLA)",
                                    "image": "https://vacc-euc.org/img/EURE.png"
                                },
                                "S": {
                                    "title": "EURS sector files",
                                    "value1": "- **EURS sector file repository:** [click here](http://files.aero-nav.com/EURO)\n- **EURS VOR & NDB list:** [click here](https://vacc-euc.org/files/VORNDB_EURS.pdf)",
                                    "value2": "- **Frequency:** `135.550`\n- **FIRs covered:** Cyprus (Nicosia/LCCC), Greece (Athinai/LGGG), Italy (Milano/LIMM, Roma/LIRR, Brandisi/LIBB), Malta (Malta/LMMM), Turkey (Istanbul/LTBB, Ankara/LTAA)",
                                    "image": "https://vacc-euc.org/img/EURS.png"
                                },
                                "M": {
                                    "title": "EURM sector files",
                                    "value1": "- **EURM sector file repository:** [click here](http://files.aero-nav.com/EURO)\n- **EURM VOR & NDB list:** [click here](https://vacc-euc.org/files/VORNDB_EURM.pdf)\n- **EURM LOAs:** [click here](https://files.flying-fox.de/forum/vatsim/eucvacc_permanent/HOS_EURM_V4.1.pdf)\n- **Handover suggestion:** [click here](https://vacc-euc.org/eurm/download)",
                                    "value2": "- **Frequency:** `135.450`\n- **FIRs covered:** Austria (Vienna/LOVV), Belgium (Brussels/EBBU), Czech Republic (Prag/LKAA), France (Reims/LFEE), Germany (Langen/EDGG, Munich/EDMM, Bremen/EDWW), Switzerland/LSAS, The Netherlands (Amsterdam/EHAA)",
                                    "image": "https://vacc-euc.org/img/EURM.png"
                                }
                            }

                            if self.letter_react[payload.emoji.name] in sf_embed_data:
                                sf_key = sf_embed_data[self.letter_react[payload.emoji.name]]
                                embed = discord.Embed(color=embed_colour)
                                embed.set_author(name="Sector files")
                                embed.add_field(name=sf_key["title"], value=sf_key["value1"], inline=False)
                                embed.add_field(name="**Additional information**", value=sf_key["value2"], inline=False)
                                embed.set_image(url=sf_key["image"])

                                await target_message.delete()
                                new_msg = await target_channel.send(embed=embed)
                                await new_msg.add_reaction("\U0001f534")
                                old_l = []
                                old_l.append(r_message_id)
                                RTracker().retireMessages(old_l)
                                RTracker().addMessage(int(new_msg.id), "SF", f"CH2 {r_user_id} {r_channel_id}")
                                return
                            else:
                                target_user = self.client.get_user(int(m_target_user))
                                await target_message.remove_reaction(payload.emoji, target_user)
                                return
                            
                    
                    elif m_state == "CH2":
                        target_channel = self.client.get_channel(int(m_target_channel))
                        target_message = await target_channel.fetch_message(int(r_message_id))
                        if payload.emoji.name == "\U0001f534":
                            await target_message.delete()
                            old_l = []
                            old_l.append(r_message_id)
                            RTracker().retireMessages(old_l)
                        else:
                            target_user = self.client.get_user(int(m_target_user))
                            await target_message.remove_reaction(payload.emoji, target_user)
                            return


def setup(client):
    client.add_cog(reactionsAdd(client))