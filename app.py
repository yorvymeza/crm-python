from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Client, Deal
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
# Nombre de la base de datos crm.db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crm.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
def dashboard():
    # Get basic stats
    total_clients = Client.query.count()
    total_deals = Deal.query.count()
    total_value = db.session.query(db.func.sum(Deal.value)).scalar() or 0
    
    # Get deals by stage
    stages = ['prospect', 'qualified', 'proposal', 'negotiation', 'closed_won', 'closed_lost']
    deals_by_stage = {}
    for stage in stages:
        deals_by_stage[stage] = Deal.query.filter_by(stage=stage).count()
    
    # Recent deals
    recent_deals = Deal.query.order_by(Deal.updated_at.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                         total_clients=total_clients,
                         total_deals=total_deals,
                         total_value=total_value,
                         deals_by_stage=deals_by_stage,
                         recent_deals=recent_deals)

@app.route('/clients')
def clients():
    clients_list = Client.query.order_by(Client.created_at.desc()).all()
    return render_template('clients.html', clients=clients_list)

@app.route('/clients/new', methods=['GET', 'POST'])
def new_client():
    if request.method == 'POST':
        client = Client(
            name=request.form['name'],
            email=request.form['email'],
            phone=request.form['phone'],
            company=request.form['company'],
            status=request.form['status']
        )
        db.session.add(client)
        db.session.commit()
        flash('Client created successfully!', 'success')
        return redirect(url_for('clients'))
    
    return render_template('client_form.html', client=None)

@app.route('/clients/<int:client_id>/edit', methods=['GET', 'POST'])
def edit_client(client_id):
    client = Client.query.get_or_404(client_id)
    
    if request.method == 'POST':
        client.name = request.form['name']
        client.email = request.form['email']
        client.phone = request.form['phone']
        client.company = request.form['company']
        client.status = request.form['status']
        
        db.session.commit()
        flash('Client updated successfully!', 'success')
        return redirect(url_for('clients'))
    
    return render_template('client_form.html', client=client)

@app.route('/clients/<int:client_id>/delete')
def delete_client(client_id):
    client = Client.query.get_or_404(client_id)
    db.session.delete(client)
    db.session.commit()
    flash('Client deleted successfully!', 'success')
    return redirect(url_for('clients'))

@app.route('/deals')
def deals():
    deals_list = Deal.query.order_by(Deal.updated_at.desc()).all()
    return render_template('deals.html', deals=deals_list)

@app.route('/deals/new', methods=['GET', 'POST'])
def new_deal():
    clients = Client.query.all()
    
    if request.method == 'POST':
        expected_close = None
        if request.form['expected_close']:
            expected_close = datetime.strptime(request.form['expected_close'], '%Y-%m-%d').date()
            
        deal = Deal(
            title=request.form['title'],
            description=request.form['description'],
            value=float(request.form['value'] or 0),
            stage=request.form['stage'],
            probability=int(request.form['probability'] or 0),
            expected_close=expected_close,
            client_id=int(request.form['client_id'])
        )
        db.session.add(deal)
        db.session.commit()
        flash('Deal created successfully!', 'success')
        return redirect(url_for('deals'))
    
    return render_template('deal_form.html', deal=None, clients=clients)

@app.route('/deals/<int:deal_id>/edit', methods=['GET', 'POST'])
def edit_deal(deal_id):
    deal = Deal.query.get_or_404(deal_id)
    clients = Client.query.all()
    
    if request.method == 'POST':
        deal.title = request.form['title']
        deal.description = request.form['description']
        deal.value = float(request.form['value'] or 0)
        deal.stage = request.form['stage']
        deal.probability = int(request.form['probability'] or 0)
        deal.client_id = int(request.form['client_id'])
        
        if request.form['expected_close']:
            deal.expected_close = datetime.strptime(request.form['expected_close'], '%Y-%m-%d').date()
        else:
            deal.expected_close = None
            
        db.session.commit()
        flash('Deal updated successfully!', 'success')
        return redirect(url_for('deals'))
    
    return render_template('deal_form.html', deal=deal, clients=clients)

@app.route('/deals/<int:deal_id>/delete')
def delete_deal(deal_id):
    deal = Deal.query.get_or_404(deal_id)
    db.session.delete(deal)
    db.session.commit()
    flash('Deal deleted successfully!', 'success')
    return redirect(url_for('deals'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)