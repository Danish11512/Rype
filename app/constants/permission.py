# Visitor Permissions - 
ORDER = 0x000000001
PAY = 0x000000002

# Customer Permissions - Can order, Pay, and comment on food 
COMMENT = 0x000000004

# Delivery Person Permissions - Bid, choose routes, comment on customer 
BID = 0x000000008
ROUTES = 0x000000010
CUSTOMER_COMMENT = 0x000000020

# Cook Permissions - food quality, menu, prices 
FOOD_QUALITY = 0x000000040
MENU = 0x000000080
PRICES = 0x000000100

# Salesperson Permissions - Nagotiate with Supplier
SUPPLIER = 0x000000200

# Manager Permissions - commissions for sales, pay for cooks, complaints, management of customers
COMMISSIONS = 0x000000400
PAY = 0x000000800
COMPLAINTS = 0x000000800
MANAGEMENT = 0x000001000

