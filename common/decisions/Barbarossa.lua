GER_industry_relocation = {

	GER_relocate_industry_from_moscow = {
        name = GER_capture_equipment 
		icon = generic_industry

		is_good = no

		days_mission_timeout = 50

		highlight_state_targets = { state = 219 } 
		
		selectable_mission = no	

		activation = {
            SOV = {
		    	has_idea = SOV_relocating_industry
            }
		}
		available = {
			NOT = {
				219 = { #Moscow
					is_owned_and_controlled_by = SOV
				} 
			}
		}

		fire_only_once = yes

		complete_effect = {
			add_equipment_to_stockpile = {
				type = infantry_equipment_1
				amount = 5000
				producer = SOV
			}	
			add_equipment_to_stockpile = {
				type = support_equipment
				amount = 300
				producer = SOV
			}
			add_equipment_to_stockpile = {
				type = radio_equipment
				amount = 300
				producer = SOV
			}
			add_equipment_to_stockpile = {
				type = artillery_equipment_1
				amount = 500
				producer = SOV
			}
            
		}
	}

	GER_relocate_industry_from_leningrad = {
        name = GER_capture_equipment
		icon = generic_industry

		is_good = no

		
		
		days_mission_timeout = 50

		highlight_state_targets = { state = 195 } 

		selectable_mission = no

		available = {	
			NOT = {
				195 = { #Leningrad
					is_owned_and_controlled_by = SOV
				}
			}		
		}

		fire_only_once = yes

		activation = {
            SOV = {
		    	has_idea = SOV_relocating_industry
            }
		}
		complete_effect = {
			add_equipment_to_stockpile = {
				type = infantry_equipment_1
				amount = 5000
				producer = SOV
			}	
			add_equipment_to_stockpile = {
				type = support_equipment
				amount = 300
				producer = SOV
			}
			add_equipment_to_stockpile = {
				type = radio_equipment
				amount = 300
				producer = SOV
			}
			add_equipment_to_stockpile = {
				type = artillery_equipment_1
				amount = 500
				producer = SOV
			}
		}
	}
	
	GER_relocate_industry_from_dnipropetrovsk = {
        name = GER_capture_equipment
		icon = generic_industry

		is_good = no

		
		
		days_mission_timeout = 13

		highlight_state_targets = { state = 226 } 
	
		selectable_mission = no

		activation = {
            SOV = {
		    	has_idea = SOV_relocating_industry
            }
		}
		available = {
			NOT = {
				226 = { #Dnipropetrovsk
					is_owned_and_controlled_by = SOV
				}
			}			
		}

		fire_only_once = yes

		complete_effect = {
            add_equipment_to_stockpile = {
				type = infantry_equipment_1
				amount = 5000
				producer = SOV
			}	
			add_equipment_to_stockpile = {
				type = support_equipment
				amount = 300
				producer = SOV
			}
			add_equipment_to_stockpile = {
				type = radio_equipment
				amount = 300
				producer = SOV
			}
			add_equipment_to_stockpile = {
				type = artillery_equipment_1
				amount = 500
				producer = SOV
			}	
		}
	}

	GER_relocate_industry_from_cherkasy = {
        name = GER_capture_equipment 
		icon = generic_industry

		is_good = no
		
		days_mission_timeout = 13

		highlight_state_targets = { state = 203 } 
		
		selectable_mission = no

		activation = {
            SOV = {
		    	has_idea = SOV_relocating_industry
            }
		}
		available = {
			NOT = {
				203 = { #Cherkasy
					is_owned_and_controlled_by = SOV
				}
			}				
		}

		fire_only_once = yes

		complete_effect = {
			add_equipment_to_stockpile = {
				type = infantry_equipment_1
				amount = 5000
				producer = SOV
			}	
			add_equipment_to_stockpile = {
				type = support_equipment
				amount = 300
				producer = SOV
			}
			add_equipment_to_stockpile = {
				type = radio_equipment
				amount = 300
				producer = SOV
			}
			add_equipment_to_stockpile = {
				type = artillery_equipment_1
				amount = 500
				producer = SOV
			}	
		}
	}

	GER_relocate_industry_from_keiv = {
        name = GER_capture_equipment 
		icon = generic_industry

		is_good = no

		
		
		days_mission_timeout = 13

		highlight_state_targets = { state = 202 } 
		
		selectable_mission = no

		activation = {
            SOV = {
		    	has_idea = SOV_relocating_industry
            }
		}
		available = {
			NOT = {
				202 = { #Keiv
					is_owned_and_controlled_by = SOV
				}
			}			
		}

		fire_only_once = yes

		complete_effect = {
			add_equipment_to_stockpile = {
				type = infantry_equipment_1
				amount = 5000
				producer = SOV
			}	
			add_equipment_to_stockpile = {
				type = support_equipment
				amount = 300
				producer = SOV
			}
			add_equipment_to_stockpile = {
				type = radio_equipment
				amount = 300
				producer = SOV
			}
			add_equipment_to_stockpile = {
				type = artillery_equipment_1
				amount = 500
				producer = SOV
			}		
		}
	}

	GER_relocate_industry_from_rostov = {
        name = GER_capture_equipment 
		icon = generic_industry

		is_good = no

		
		
		days_mission_timeout = 27

		highlight_state_targets = { state = 218 } 
		
		selectable_mission = no

		activation = {
            SOV = {
		    	has_idea = SOV_relocating_industry
            }
		}
		available = {
			NOT = {
				218 = { #Rostov
					is_owned_and_controlled_by = SOV
				}
			}		
		}

		fire_only_once = yes

		complete_effect = {
			add_equipment_to_stockpile = {
				type = infantry_equipment_1
				amount = 5000
				producer = SOV
			}	
			add_equipment_to_stockpile = {
				type = support_equipment
				amount = 300
				producer = SOV
			}
			add_equipment_to_stockpile = {
				type = radio_equipment
				amount = 300
				producer = SOV
			}
			add_equipment_to_stockpile = {
				type = artillery_equipment_1
				amount = 500
				producer = SOV
			}		
		}
	}

	GER_relocate_industry_from_kharkov = {
        name = GER_capture_equipment 
		icon = generic_industry

		is_good = no

		
		
		days_mission_timeout = 27

		highlight_state_targets = { state = 221 } 
		
		selectable_mission = no

		activation = {
            SOV = {
		    	has_idea = SOV_relocating_industry
            }
		}
		available = {
			NOT = {
				221 = { #Kharkov
					is_owned_and_controlled_by = SOV
				}
			}		
		}

		fire_only_once = yes

		complete_effect = {
			add_equipment_to_stockpile = {
				type = infantry_equipment_1
				amount = 5000
				producer = SOV
			}	
			add_equipment_to_stockpile = {
				type = support_equipment
				amount = 300
				producer = SOV
			}
			add_equipment_to_stockpile = {
				type = radio_equipment
				amount = 300
				producer = SOV
			}
			add_equipment_to_stockpile = {
				type = artillery_equipment_1
				amount = 500
				producer = SOV
			}			

		}
	}
		
	GER_relocate_industry_from_odessa = {
        name = GER_capture_equipment 
		icon = generic_industry

		is_good = no

		
		
		days_mission_timeout = 6
		
		selectable_mission = no

		highlight_state_targets = { state = 192 } 

		activation = {
            SOV = {
		    	has_idea = SOV_relocating_industry
            }
		}
		available = {
			NOT = {
				192 = { #Odessa
					is_owned_and_controlled_by = SOV
				}
			}
		}

		fire_only_once = yes

		complete_effect = {
			add_equipment_to_stockpile = {
				type = infantry_equipment_1
				amount = 5000
				producer = SOV
			}	
			add_equipment_to_stockpile = {
				type = support_equipment
				amount = 300
				producer = SOV
			}
			add_equipment_to_stockpile = {
				type = radio_equipment
				amount = 300
				producer = SOV
			}
			add_equipment_to_stockpile = {
				type = artillery_equipment_1
				amount = 500
				producer = SOV
			}		

		}
	}

	GER_relocate_industry_from_smolensk = {
        name = GER_capture_equipment 
		icon = generic_industry

		is_good = no

		days_mission_timeout = 27
		
		selectable_mission = no

		highlight_state_targets = { state = 242 } 

		activation = {
            SOV = {
		    	has_idea = SOV_relocating_industry
            }
		}
		available = {
			NOT = {
				242 = { #Smolensk
					is_owned_and_controlled_by = SOV
				}
			}
		}

		fire_only_once = yes

		complete_effect = {
			add_equipment_to_stockpile = {
				type = infantry_equipment_1
				amount = 5000
				producer = SOV
			}	
			add_equipment_to_stockpile = {
				type = support_equipment
				amount = 300
				producer = SOV
			}
			add_equipment_to_stockpile = {
				type = radio_equipment
				amount = 300
				producer = SOV
			}
			add_equipment_to_stockpile = {
				type = artillery_equipment_1
				amount = 500
				producer = SOV
			}
		}
	}

	GER_relocate_industry_from_lwow = {
        name = GER_capture_equipment 
		icon = generic_industry

		is_good = no
	
		days_mission_timeout = 4
		
		selectable_mission = no

		highlight_state_targets = { state = 91 } 

		activation = {
            SOV = {
		    	has_idea = SOV_relocating_industry
            }
		}
		available = {
			NOT = {
				91 = { #Lwow
					is_owned_and_controlled_by = SOV
				}
			}			
		}

		fire_only_once = yes

		complete_effect = {
			add_equipment_to_stockpile = {
				type = infantry_equipment_1
				amount = 5000
				producer = SOV
			}	
			add_equipment_to_stockpile = {
				type = support_equipment
				amount = 300
				producer = SOV
			}
			add_equipment_to_stockpile = {
				type = radio_equipment
				amount = 300
				producer = SOV
			}
			add_equipment_to_stockpile = {
				type = artillery_equipment_1
				amount = 500
				producer = SOV
			}		
		}
	}

	GER_relocate_industry_from_minsk = {
        name = GER_capture_equipment 
		icon = generic_industry

		is_good = no

		
		
		days_mission_timeout = 13
		
		selectable_mission = no

		highlight_state_targets = { state = 206 } 
		
		activation = {
            SOV = {
		    	has_idea = SOV_relocating_industry
            }
		}
		available = {
			NOT = {
				206 = { #Minsk
					is_owned_and_controlled_by = SOV
				}
			}				
		}

		fire_only_once = yes

		complete_effect = {
			add_equipment_to_stockpile = {
				type = infantry_equipment_1
				amount = 5000
				producer = SOV
			}	
			add_equipment_to_stockpile = {
				type = support_equipment
				amount = 300
				producer = SOV
			}
			add_equipment_to_stockpile = {
				type = radio_equipment
				amount = 300
				producer = SOV
			}
			add_equipment_to_stockpile = {
				type = artillery_equipment_1
				amount = 500
				producer = SOV
			}			

		}
	}

	GER_relocate_industry_from_karunas = {
        name = GER_capture_equipment 
		icon = generic_industry

		is_good = no

		days_mission_timeout = 6
		
		selectable_mission = no

		highlight_state_targets = { state = 11 } 
		
		activation = {
            SOV = {
		    	has_idea = SOV_relocating_industry
            }
		}
		available = {
			NOT = {
				11 = { #Karunas
					is_owned_and_controlled_by = SOV
				}
			}			
		}

		fire_only_once = yes

		complete_effect = {
			add_equipment_to_stockpile = {
				type = infantry_equipment_1
				amount = 5000
				producer = SOV
			}	
			add_equipment_to_stockpile = {
				type = support_equipment
				amount = 300
				producer = SOV
			}
			add_equipment_to_stockpile = {
				type = radio_equipment
				amount = 300
				producer = SOV
			}
			add_equipment_to_stockpile = {
				type = artillery_equipment_1
				amount = 500
				producer = SOV
			}		

		}
	}

	GER_relocate_industry_from_vidzeme = {
        name = GER_capture_equipment 
		icon = generic_industry

		is_good = no

		days_mission_timeout = 13
		
		selectable_mission = no

		activation = {
            SOV = {
		    	has_idea = SOV_relocating_industry
            }
		}

		available = {
			NOT = {
				12 = { #Vidzeme
					is_owned_and_controlled_by = SOV
				}
			}			
		}

		highlight_state_targets = { state = 12 } 

		fire_only_once = yes

		complete_effect = {
			add_equipment_to_stockpile = {
				type = infantry_equipment_1
				amount = 5000
				producer = SOV
			}	
			add_equipment_to_stockpile = {
				type = support_equipment
				amount = 300
				producer = SOV
			}
			add_equipment_to_stockpile = {
				type = radio_equipment
				amount = 300
				producer = SOV
			}
			add_equipment_to_stockpile = {
				type = artillery_equipment_1
				amount = 500
				producer = SOV
			}	

		}
	}

	GER_relocate_industry_from_harju = {
        name = GER_capture_equipment 
		icon = generic_industry

		is_good = no

		days_mission_timeout = 23
		
		selectable_mission = no
		
		activation = {
            SOV = {
		    	has_idea = SOV_relocating_industry
            }
		}
		available = {
			NOT = {
				13 = { #Harju
					is_owned_and_controlled_by = SOV
				}
			}			
		}

		highlight_state_targets = { state = 13 } 

		fire_only_once = yes

		complete_effect = {
			add_equipment_to_stockpile = {
				type = infantry_equipment_1
				amount = 5000
				producer = SOV
			}	
			add_equipment_to_stockpile = {
				type = support_equipment
				amount = 300
				producer = SOV
			}
			add_equipment_to_stockpile = {
				type = radio_equipment
				amount = 300
				producer = SOV
			}
			add_equipment_to_stockpile = {
				type = artillery_equipment_1
				amount = 500
				producer = SOV
			}
		}
	}

	GER_relocate_industry_from_tartu = {
        name = GER_capture_equipment 
		icon = generic_industry

		is_good = no

		days_mission_timeout = 23
		
		selectable_mission = no

		highlight_state_targets = { state = 191 } 

		activation = {
            SOV = {
		    	has_idea = SOV_relocating_industry
            }
		}
		available = {
			NOT = {
				191 = { #Tartu
					is_owned_and_controlled_by = SOV
				}
			}		
		}

		fire_only_once = yes

		complete_effect = {
			add_equipment_to_stockpile = {
				type = infantry_equipment_1
				amount = 5000
				producer = SOV
			}	
			add_equipment_to_stockpile = {
				type = support_equipment
				amount = 300
				producer = SOV
			}
			add_equipment_to_stockpile = {
				type = radio_equipment
				amount = 300
				producer = SOV
			}
			add_equipment_to_stockpile = {
				type = artillery_equipment_1
				amount = 500
				producer = SOV
			}	

		}
	}

	GER_relocate_industry_from_karjala = {
        name = GER_capture_equipment 
		icon = generic_industry

		is_good = no

		days_mission_timeout = 27
		
		selectable_mission = no

		highlight_state_targets = { state = 146 } 

		activation = {
            SOV = {
		    	has_idea = SOV_relocating_industry
            } 
		}
		available = {
			NOT = {
				146 = { #Karjala
					is_owned_and_controlled_by = SOV
				}
			}			
		}

		fire_only_once = yes

		complete_effect = {
			add_equipment_to_stockpile = {
				type = infantry_equipment_1
				amount = 5000
				producer = SOV
			}	
			add_equipment_to_stockpile = {
				type = support_equipment
				amount = 300
				producer = SOV
			}
			add_equipment_to_stockpile = {
				type = radio_equipment
				amount = 300
				producer = SOV
			}
			add_equipment_to_stockpile = {
				type = artillery_equipment_1
				amount = 500
				producer = SOV
			}
		}
	}

	GER_relocate_industry_from_bialystok = {
        name = GER_capture_equipment 
		icon = generic_industry

		is_good = no

		days_mission_timeout = 6
		
		selectable_mission = no

		highlight_state_targets = { state = 97 } 

		activation = {
            SOV = {
		    	has_idea = SOV_relocating_industry
            }
		}
		available = {
			NOT = {
				97 = { #Bialystok
					is_owned_and_controlled_by = SOV
				}
			}		
		}

		fire_only_once = yes	

		complete_effect = {
			add_equipment_to_stockpile = {
				type = infantry_equipment_1
				amount = 5000
				producer = SOV
			}	
			add_equipment_to_stockpile = {
				type = support_equipment
				amount = 300
				producer = SOV
			}
			add_equipment_to_stockpile = {
				type = radio_equipment
				amount = 300
				producer = SOV
			}
			add_equipment_to_stockpile = {
				type = artillery_equipment_1
				amount = 500
				producer = SOV
			}		
		}
	}

	GER_relocate_industry_from_orel = {
        name = GER_capture_equipment 
		icon = generic_industry

		is_good = no
		
		days_mission_timeout = 27
		
		selectable_mission = no

		highlight_state_targets = { state = 570 } 

		activation = {
            SOV = {
		    	has_idea = SOV_relocating_industry
            }
		}
		available = {
			NOT = {
				570 = { is_owned_and_controlled_by = SOV } #Novosibirsk
			}	
		}

		fire_only_once = yes

		complete_effect = {
			add_equipment_to_stockpile = {
				type = infantry_equipment_1
				amount = 5000
				producer = SOV
			}	
			add_equipment_to_stockpile = {
				type = support_equipment
				amount = 300
				producer = SOV
			}
			add_equipment_to_stockpile = {
				type = radio_equipment
				amount = 300
				producer = SOV
			}
			add_equipment_to_stockpile = {
				type = artillery_equipment_1
				amount = 500
				producer = SOV
			}
		}
	}

	GER_relocate_industry_from_tula = {
        name = GER_capture_equipment 
		icon = generic_industry

		is_good = no

		days_mission_timeout = 37
		
		selectable_mission = no

		activation = {
            SOV = {
		    	has_idea = SOV_relocating_industry
            }
		}
		available = {
			NOT = {
				223 = { #Tula
					is_owned_and_controlled_by = SOV
				}
			}
		}

		highlight_state_targets = { state = 223 } 

		fire_only_once = yes

		complete_effect = {
			add_equipment_to_stockpile = {
				type = infantry_equipment_1
				amount = 5000
				producer = SOV
			}	
			add_equipment_to_stockpile = {
				type = support_equipment
				amount = 300
				producer = SOV
			}
			add_equipment_to_stockpile = {
				type = radio_equipment
				amount = 300
				producer = SOV
			}
			add_equipment_to_stockpile = {
				type = artillery_equipment_1
				amount = 500
				producer = SOV
			}		

		}
	}

	GER_relocate_industry_from_rzhev = {
        name = GER_capture_equipment 
		icon = generic_industry

		is_good = no

		days_mission_timeout = 37
		
		selectable_mission = no

		activation = {
            SOV = {
		    	has_idea = SOV_relocating_industry
            }
		}
		available = {
			NOT = {
				246 = { #Rzhev
					is_owned_and_controlled_by = SOV
				}
			}	
		}

		highlight_state_targets = { state = 246 } 

		fire_only_once = yes

		complete_effect = {
			add_equipment_to_stockpile = {
				type = infantry_equipment_1
				amount = 5000
				producer = SOV
			}	
			add_equipment_to_stockpile = {
				type = support_equipment
				amount = 300
				producer = SOV
			}
			add_equipment_to_stockpile = {
				type = radio_equipment
				amount = 300
				producer = SOV
			}
			add_equipment_to_stockpile = {
				type = artillery_equipment_1
				amount = 500
				producer = SOV
			}			
		}
	}
}	
	