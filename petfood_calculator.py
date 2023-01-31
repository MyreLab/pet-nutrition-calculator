# January 2023
# Myrela Bauman

# ************** Euclid & Watson Dry/Wet food calculator *************** #

import pandas as pd
import itertools
from sklearn.linear_model import LinearRegression 

#
# Importing data: 
#

url = 'https://github.com/MyreLab/petfood_calculator/blob/main/nutrition.xlsx?raw=true'

# ***** For Euclid 🐻‍❄️ ***** # 
# Purina One: Natural SmartBlend Chicken & Rice, Large Breed, Dry Dog Food
purina = pd.read_excel(url, sheet_name='Purina_Nutrition')

# modifying the purina dataframe by adding a new column that contains the number of cups per lb of bodyweight based
# on each weight range
purina['cups_per_lbs'] = (purina.amount_low/purina.weight_low + purina.amount_high/purina.weight_high)/2

# ***** For Watson 🐈‍⬛ ***** #
# Royal Canin Urinary SO
watson_wet = pd.read_excel(url, sheet_name='Watson_wet')
watson_dry = pd.read_excel(url, sheet_name='Watson_dry')

# For Watson, need to fit a linear regression to calculate the grams of wet and dry food required per
# lbs of body weight

watson_wet_part = watson_wet[['weight_lbs','normal_weight_gramsperday']]

X = watson_wet_part[['weight_lbs']]
y = watson_wet_part['normal_weight_gramsperday']

watson_wet_model = LinearRegression().fit(X,y)

watson_dry_part = watson_dry[['weight_lbs','normal_weight_gramsperday']]

X = watson_dry_part[['weight_lbs']]
y = watson_dry_part['normal_weight_gramsperday']

watson_dry_model = LinearRegression().fit(X,y)

# ----------------------------------------------------- #
# Creating prompts to guide user when running the program
# ----------------------------------------------------- #


#meow_or_woof stores the names Euclid and Watson
meow_or_woof = input('Who are you calculating food quantities for? Type "Euclid" or "Watson" ')

#chonk stores the weight
chonk = int(input(f'How much does {meow_or_woof} weigh (lbs)? '))

#diet_type offers 3 diet options: dry only, wet only, or combination
diet_type = input(f'What type of diet will {meow_or_woof} have? Type "dry only", "wet only", or "combination" ')

#defining target amount of wet or dry food in a combination diet
if diet_type == 'combination':
    constraint_type = input('Do you want to restrict the amount of wet food or dry food? Type "wet", "dry", otherwise type "no": ')
    if constraint_type == 'wet':
        wet_limit = int(input('Enter target number of cans of wet food: '))
    elif constraint_type == 'dry':
        dry_limit = int(input('Enter target number of cups/scoops of dry food: '))    


# ------------------------ #
# ------Calculations------ #
# ------------------------ #

# Creating function to calculate amount of food required for "dry only" diet based on pet weight

def dry_only(chonk):
    
    if meow_or_woof == 'Euclid':
            
        for (low, high) in zip(purina.weight_low, purina.weight_high):
            if chonk >= low and chonk <= high:
                cups_needed = purina.cups_per_lbs[purina.index[purina['weight_high'] == high].item()]
                dry_only = round(cups_needed * chonk,1) #cups needed * weight, rounded to 1 decimal places
            
    elif meow_or_woof == 'Watson':
        grams_dry = chonk*int(watson_dry_model.coef_) + int(watson_dry_model.intercept_) #using linear regression results here
        dry_only = round(grams_dry/15,1) # 15g per scoop based on the scoop we use
    
    return dry_only


# Creating function to calculate amount of food required for "wet only" diet based on pet weight

def wet_only(chonk):
    
    if meow_or_woof == 'Euclid':
    
    # cans_needed formula represents the feeding instructions on the back of the can
    # these say that 0.75 to 1 cup of wet food are required per 15 lbs of weight, we average the cup requirement here
    
        cans_needed = ((0.75+1)/2)/15
        wet_only = round(chonk * cans_needed,1)
    
    elif meow_or_woof == 'Watson':
        grams_wet = chonk*int(watson_wet_model.coef_) + int(watson_wet_model.intercept_) #using linear regression results here
        wet_only = round(grams_wet / 85,1) # number of cans based on a single can being 85g
            
    return wet_only

# **************** #
# **** Euclid **** #
# **************** #

# calculation for combination diet
if meow_or_woof == 'Euclid':
    
    if diet_type == 'combination':
        if constraint_type == 'dry':
            
# dry_deficit is the difference between the amount of food given by the dry_only function and
# the dry_limit set by the user. The deficit is used to calculate the equivalent amount of wet
# to make up the remainder of the caloric intake. For every 1/3 cup of dry food in the
# dry_deficit we add 6oz of wet food. The division by 13 transforms the weight of wet food
# into number of cans of wet food (each can contains 13oz)

            dry_deficit = dry_only(chonk) - dry_limit
            wet_required = round((dry_deficit/(1/3)) * 6/13,1)
            
            print(f'Feed {meow_or_woof} {wet_required} can(s) of wet food and {dry_limit} cups of dry food')
        
        elif constraint_type == 'wet':
            
# reduction_amount is the amount of dry food to reduce to compensate for the wet food
# the value given on the back of the can is reduce 1/3 cup of dry food per 6 oz of wet food
# each can of wet food contains 13 oz, this needs to change if we change brand of wet food  
            
            reduction_amount = (1/3) * (wet_limit * 13)/6  #cups of dry food
            dry_food_combination = round(dry_only(chonk) - reduction_amount,1)
            
            print(f'Feed {meow_or_woof} {wet_limit} can of wet food and {dry_food_combination} cups of dry food per day ')
        
        else:
            
            print(f'Feed {meow_or_woof} {wet_only(chonk)/2} can(s) of wet food and {dry_only(chonk)/2} cups of dry food per day ')
        
        #calculating for dry only or wet only diet:
    elif diet_type == 'dry only':
        dry_only(chonk)
    else:
        wet_only(chonk)

# **************** #        
# **** Watson **** #
# **************** #

# calculation for combination diet
elif meow_or_woof == 'Watson':
    
    if diet_type == 'combination':
        if constraint_type == 'dry':
            
            # figure out how much wet food required based on the proportion of daily intake
            # "left over" from limiting the dry food intake and compensating with wet food
            wet_required = (1 - (dry_limit/dry_only(chonk))) * wet_only(chonk)
            
            print(f'Feed {meow_or_woof} {wet_required} can(s) of wet food and {dry_limit} scoops of dry food')
        
        elif constraint_type == 'wet':
            
            # figure out how much dry food required based on the proportion of daily intake
            # "left over" from limiting the wet food intake and compensating with dry food
            dry_required = (1 - (wet_limit/wet_only(chonk))) * dry_only(chonk)
            
            print(f'Feed {meow_or_woof} {wet_limit} can of wet food and {dry_food_combination} scoops of dry food per day ')
        
        else:
            
            # if no constraint type is selected, then just do a 50/50 mix of wet and dry
            print(f'Feed {meow_or_woof} {wet_only(chonk)/2} can(s) of wet food and {dry_only(chonk)/2} cups of dry food per day ')

    #calculating for dry only or wet only diet:
    elif diet_type == 'dry only':
        
        dry_only(chonk)
        
    else:
        
        wet_only(chonk)

