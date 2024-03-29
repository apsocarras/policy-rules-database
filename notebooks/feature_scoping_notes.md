see comments 

<!-- #     FATES = False
# if "APPLY_FRSP" not in globals():
#     APPLY_FRSP = False

### RESUME PLAN (3/27)
# For the dashboard, you really just need to know how the different variables
# in the dataframe relate to each other, such that if one changes you know how the others will 

## You want to be able for a user to move where a benefits program cuts off, or 
## change its slope, etc., and affect the netresources curve -- that doesn't require digging into the code 

## You also want to be able to move the income curve around and affect the net resources curve (that doesn't require it either)

## Really, to modify the base level calculator, the main advantages are for displaying/analyzing multiple beneficiary profiles  
# 1.) run it on multiple beneficiary profiles at the same time (in the same pass-through/iteration)
# 2.) know based on differences in parameters between beneficiary profiles which variables would change,
# and only run it for those variables on the next run of the loop (also useful for interactivity/quickly changing profiles)
# 3.) parallelize? 

## In any case the R code is difficult to read b/c it's copy-pasted stuff over and over 
# (e.g. look at function.CCDFcopay, they're copy-pasting the same blocks of code and changing a variable for the state dataframe,
# without it being clear what/if anything else is really changing between states)
# (look at the "Disregard Co-Pay" block, it's copy pasting over and over and passing through the dataframe way more times than necessary)

## Only in number #2 above would we want to be able to modularize everything properly. 
## That's a more advanced use case than I think we need right now.  

## Going through code right now to extract qualification rules for benefits programs is more useful.

## ---- ## 
# Functions change/recalculate based on changes in profile 
    
## Expenses 
    
    # childcareExp.ALICE: 

        # Creates dataframe of years and counties   
            # Finds years of rules to use in calculations from rules dataframe (exp.childcareData.ALICE$yearofdata) which apply to years in profile data 
                #  past years: uses closest applicable year for missing years   
                #  future years: forward-fills dataframe ith most recent year rule  
        # Merges with expense dataframe by county and year
        
        # Creates child care column (0), careduringsummer(.5 if schoolagesummercare == "PT", 1 if schoolagesummercare  == "FT") (config parameter not used in current script)
        # Creates columns for TotalInfants (<=2), TotalPreSchoolers (3 or 4), TotalSchoolAge ([5,12]) in profile
        # Calculates per-child-type expenses based on budget.ALICE== "survivalforcliff" or budget.ALICE== "stability" (using cliff)
            # FORMULAS: full-time daily childcare rate X (number of summer childcare days + number of school days) 
                # exp.childcareInfants: infant rate, 
                # exp.childcarePreSchoolers: 4yr-old rate, 
                # ALICE.exp.childcareSchoolAge:  exp.childcarePreSchoolers * (3/8)
                # exp.childcareSchoolAge: (4yr-old rate * number summer childcare days * careduringsummer) + (4yr-old rate * number of school days * .5), 
                # exp.childcare = exp.childcareInfants+exp.childcarePreSchoolers+exp.childcareSchoolAge
                # ALICE.exp.childcare = exp.childcareInfants+exp.childcarePreSchoolers+ALICE.exp.childcareSchoolAge
        # Calculates totals from these by multiplying by TotalInfants, TotalPreSchoolers, TotalSchoolAge respectively and summing
            # data$ALICE.exp.childcare<-data$exp.childcareInfants*data$TotalInfants + data$exp.childcarePreSchoolers*data$TotalPreSchoolers + data$ALICE.exp.childcareSchoolAge*data$TotalSchoolAge
            # data$exp.childcare<-data$exp.childcareInfants*data$TotalInfants + data$exp.childcarePreSchoolers*data$TotalPreSchoolers + data$exp.childcareSchoolAge*data$TotalSchoolAge
        # Create "per-person" childcare cost columns filling by person age (exp.childcareInfants, exp.childcarePreSchoolers,exp.childcareSchoolAge)
            # person1childcare = case_when(agePerson1 %in% c(0:2) ~ exp.childcareInfants
                                     #   ,agePerson1 %in% c(3:4) ~ exp.childcarePreSchoolers
                                     #   ,agePerson1 %in% c(5:12) ~ exp.childcareSchoolAge
                                     #   ,TRUE ~ 0)
            # i.e. it's a column indicating whether personN has a cost of exp.childcareInfants/exp.childcarePreSchoolers/exp.childcareSchoolAge
        # Inflates/rounds costs (to current year)
            # data$ALICE.exp.childcare<-data$ALICE.exp.childcare*(1+(.021-parameters.defaults$inflationrate[1]))^(data$Year-data$yearofdata)
            # data$exp.childcare<-data$exp.childcare*(1+(parameters.defaults$inflationrate[1]))^(data$Year-data$yearofdata)
            # data$person1childcare<-round(data$person1childcare*(1+(parameters.defaults$inflationrate[1]))^(data$ruleYear-data$yearofdata),0)
        
        # Returns dataframe of per-person childcare columns and totals, per county 




## Benefits 

## ---- ## 
# Functions to  write  
    





## ---- ## 

# ## Load table .rdata object (really just county names) for this file 
# ## These people don't know what loops are 

# def createData(inputs:dict):
#     """Create base DataFrame from profile dict (project .YAML)"""

#     if inputs['locations'] == 'all':  --> -->
