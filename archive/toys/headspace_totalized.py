def totalize_gases(total_req, o2_pc_req, co2_pc_req, n2_pc_req):
    
    # raw LPM req
    o2_req = o2_pc_req * total_req
    co2_req = co2_pc_req * total_req
    n2_req = n2_pc_req * total_req
    
    # throttle by MFC max
    o2_req = min(o2_req, o2_mfc_max)       
    co2_req = min(co2_req, co2_mfc_max)
    n2_req = min(n2_req, n2_mfc_max)
  
    # post MFC throttle % output
    o2_pc_req = o2_req / total_req
    co2_pc_req = co2_req / total_req
    n2_pc_req = n2_req / total_req
    
    # Auto/manual max % throttles
    o2_pc_req = do_ctlr_throttle_o2(o2_pc_req, do_mode)
    co2_pc_req = ph_ctlr_throttle_co2(co2_pc_req, ph_mode)
    n2_pc_req = do_ctlr_throttle_n2(n2_pc_req, do_mode)
    
    # calculate "totalized" gas flows in order, summing
    # % of total flow. 
    co2_totalized_pc = co2_pc_req
    gas_sum_pc = co2_totalized_pc
    o2_totalized_pc = max(100 - gas_sum_pc, o2_pc_req)
    gas_sum_pc += o2_totalized_pc
    n2_totalized_pc  = max(100 - gas_sum_pc, n2_pc_req)
    gas_sum_pc += n2_totalized_pc
    air_totalized_pc = 100 - gas_sum_pc
    
    assert co2_totalized_pc + o2_totalized_pc + n2_totalized_pc + air_totalized_pc == 100, "oops"
    
    # calculate actual MFC output
    co2_flow_actual_lpm = total_req * co2_totalized_pc
    n2_flow_actual_lpm = total_req * n2_totalized_pc
    air_flow_actual_lpm = total_req * air_totalized_pc
    o2_flow_actual_lpm = total_req * o2_totalized_pc

    # o2 slow start throttle
    if slow_start:
        o2_req_limited = o2_flow_actual_lpm
    else:
        o2_req_limited = o2_flow_actual_lpm
    
    # for fun, the "actual %" outputs coerced to % 
    # of main gas total
    gff = total_req / (co2_flow_actual_lpm + n2_flow_actual_lpm + air_flow_actual_lpm)
    co2_flow_actual_lpm = gff * co2_totalized_pc
    n2_flow_actual_lpm = gff * n2_totalized_pc
    air_flow_actual_lpm = gff * air_totalized_pc
    
    mfc_output = calc_mfc_output(co2_flow_actual_lpm, n2_flow_actual_lpm, air_flow_actual_lpm, o2_req_limited)
    user_display = calc_user_display(co2_totalized_pc, n2_totalized_pc, air_totalized_pc, o2_totalized_pc)
    
    return mfc_output, user_display

def calc_mfc_output(*args):
    return args

def calc_user_display(*args):
    return args
