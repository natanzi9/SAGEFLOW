from datetime import date, timedelta
from app import db
from app.models import User, Account, Card, Transaction, Budget, Goal, Investment, BillPayable, BillReceivable

def seed_database():
    # Check if a user already exists
    if User.query.first() is not None:
        return # Database already seeded
        
    print("Seeding database with demo data...")
    
    # 1. Create Demo User
    demo_user = User(username="demo", email="demo@sageflow.com")
    demo_user.set_password("123")
    db.session.add(demo_user)
    db.session.flush() # Get user.id
    
    # 2. Create Accounts
    itau = Account(user_id=demo_user.id, name="Itaú Corrente", type="Conta Corrente", balance=3450.00)
    nubank_savings = Account(user_id=demo_user.id, name="Nubank Poupança", type="Poupança", balance=12000.00)
    mercado_pago = Account(user_id=demo_user.id, name="Mercado Pago Wallet", type="Carteira Digital", balance=450.00)
    
    db.session.add_all([itau, nubank_savings, mercado_pago])
    db.session.flush()
    
    # 3. Create Credit Card
    nubank_card = Card(
        user_id=demo_user.id,
        name="Nubank Mastercard Gold",
        limit=5000.00,
        due_day=5,
        closing_day=28,
        current_spend=1240.00
    )
    db.session.add(nubank_card)
    db.session.flush()
    
    # 4. Create Budgets
    food_budget = Budget(user_id=demo_user.id, category="Alimentação", amount_limit=800.00, current_spent=450.00)
    transp_budget = Budget(user_id=demo_user.id, category="Transporte", amount_limit=300.00, current_spent=120.00)
    leisure_budget = Budget(user_id=demo_user.id, category="Lazer", amount_limit=500.00, current_spent=250.00)
    
    db.session.add_all([food_budget, transp_budget, leisure_budget])
    
    # 5. Create Goals
    vacation = Goal(
        user_id=demo_user.id,
        name="Viagem para Maceió",
        target_amount=10000.00,
        current_amount=4500.00,
        deadline=date.today() + timedelta(days=180)
    )
    emergency = Goal(
        user_id=demo_user.id,
        name="Reserva de Emergência",
        target_amount=20000.00,
        current_amount=8000.00
    )
    db.session.add_all([vacation, emergency])
    
    # 6. Create Investments
    tesouro = Investment(
        user_id=demo_user.id,
        name="Tesouro Selic 2029",
        type="Tesouro Direto",
        amount=5000.00,
        purchase_date=date.today() - timedelta(days=45)
    )
    cdb = Investment(
        user_id=demo_user.id,
        name="CDB Itaú 120% CDI",
        type="CDB",
        amount=3000.00,
        purchase_date=date.today() - timedelta(days=20)
    )
    db.session.add_all([tesouro, cdb])
    
    # 7. Create Bills
    bill1 = BillPayable(
        user_id=demo_user.id,
        name="Conta de Luz - Light",
        amount=180.00,
        due_date=date.today() + timedelta(days=6),
        status="pending"
    )
    bill2 = BillPayable(
        user_id=demo_user.id,
        name="Internet Claro Fibra",
        amount=120.00,
        due_date=date.today() + timedelta(days=9),
        status="pending"
    )
    bill3 = BillPayable(
        user_id=demo_user.id,
        name="Aluguel Mensal",
        amount=1800.00,
        due_date=date.today() + timedelta(days=1),
        status="pending"
    )
    
    rec1 = BillReceivable(
        user_id=demo_user.id,
        name="Salário Mensal",
        amount=5000.00,
        expected_date=date.today() + timedelta(days=22),
        status="pending"
    )
    rec2 = BillReceivable(
        user_id=demo_user.id,
        name="Freelance Design",
        amount=850.00,
        expected_date=date.today() + timedelta(days=4),
        status="pending"
    )
    
    db.session.add_all([bill1, bill2, bill3, rec1, rec2])
    
    # 8. Create Transactions (Historical & Current Month)
    # Current month tx
    t1 = Transaction(
        user_id=demo_user.id,
        account_id=itau.id,
        type="income",
        category="Salário",
        amount=5000.00,
        description="Salário Mensal de Maio",
        date=date.today() - timedelta(days=8)
    )
    t2 = Transaction(
        user_id=demo_user.id,
        account_id=itau.id,
        type="expense",
        category="Alimentação",
        amount=450.00,
        description="Supermercado Zona Sul",
        date=date.today() - timedelta(days=7)
    )
    t3 = Transaction(
        user_id=demo_user.id,
        account_id=itau.id,
        type="expense",
        category="Transporte",
        amount=120.00,
        description="Combustível Posto Ipiranga",
        date=date.today() - timedelta(days=5)
    )
    t4 = Transaction(
        user_id=demo_user.id,
        card_id=nubank_card.id,
        type="expense",
        category="Lazer",
        amount=250.00,
        description="Jantar Coco Bambu",
        date=date.today() - timedelta(days=3)
    )
    t5 = Transaction(
        user_id=demo_user.id,
        account_id=mercado_pago.id,
        type="income",
        category="Salário",
        amount=1200.00,
        description="Freelance Landing Page",
        date=date.today() - timedelta(days=4)
    )
    
    # Historical tx (for 6-month reports)
    db.session.add_all([t1, t2, t3, t4, t5])
    
    # Generate transactions for past 5 months
    for i in range(1, 6):
        month_diff = i * 30
        past_date = date.today() - timedelta(days=month_diff)
        
        # Monthly Salary
        sal = Transaction(
            user_id=demo_user.id,
            account_id=itau.id,
            type="income",
            category="Salário",
            amount=5000.00,
            description="Salário Mensal",
            date=past_date.replace(day=1)
        )
        
        # Monthly Expenses
        superm = Transaction(
            user_id=demo_user.id,
            account_id=itau.id,
            type="expense",
            category="Alimentação",
            amount=600.00 + (i * 20),
            description="Supermercado Mensal",
            date=past_date.replace(day=5)
        )
        
        transp = Transaction(
            user_id=demo_user.id,
            account_id=itau.id,
            type="expense",
            category="Transporte",
            amount=150.00 + (i * 10),
            description="Combustível",
            date=past_date.replace(day=12)
        )
        
        fun = Transaction(
            user_id=demo_user.id,
            account_id=mercado_pago.id,
            type="expense",
            category="Lazer",
            amount=300.00 - (i * 15),
            description="Cinema e Restaurantes",
            date=past_date.replace(day=20)
        )
        
        db.session.add_all([sal, superm, transp, fun])
        
    db.session.commit()
    print("Database successfully seeded!")
