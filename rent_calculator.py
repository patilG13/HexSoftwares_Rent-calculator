import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import datetime
import json
import os

class RentCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("🏠  Rent Calculator")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f5f7fa')

        self.colors = {
            'primary': '#4a6fa5',
            'secondary': '#166088',
            'accent': '#32a852',
            'danger': '#e74c3c',
            'warning': '#f39c12',
            'success': '#27ae60',
            'light': '#ecf0f1',
            'dark': '#2c3e50',
            'background': '#f5f7fa',
            'card': '#ffffff'
        }
        
        self.rent_data = {
            'rent_amount': 0,
            'utilities': {},
            'tenants': [],
            'split_type': 'equal',
            'security_deposit': 0,
            'maintenance': 0
        }
        
        self.load_data()
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg=self.colors['background'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        header_frame = tk.Frame(main_frame, bg=self.colors['primary'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        header_label = tk.Label(header_frame, text="🏠RENT CALCULATOR", 
                                font=('Helvetica', 24, 'bold'), 
                                bg=self.colors['primary'], 
                                fg='white')
        header_label.pack(pady=15)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.setup_basic_tab()
        self.setup_tenants_tab()
        self.setup_utilities_tab()
        self.setup_results_tab()
    
    def setup_basic_tab(self):
        basic_tab = tk.Frame(self.notebook, bg=self.colors['background'])
        self.notebook.add(basic_tab, text="📋 Basic Information")
        
        rent_card = self.create_card(basic_tab, "🏠 Rent Details")
        rent_card.pack(fill=tk.X, pady=10, padx=10)
        
        rent_content = tk.Frame(rent_card, bg='white')
        rent_content.pack(pady=10, padx=10)
        
        tk.Label(rent_content, text="Monthly Rent (₹):", bg='white').grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        self.rent_entry = tk.Entry(rent_content, font=('Helvetica', 11), width=15)
        self.rent_entry.grid(row=0, column=1, padx=10, pady=10)
        if self.rent_data['rent_amount'] > 0:
            self.rent_entry.insert(0, str(self.rent_data['rent_amount']))
        
        tk.Label(rent_content, text="Security Deposit (₹):", bg='white').grid(row=0, column=2, sticky=tk.W, padx=10, pady=10)
        self.deposit_entry = tk.Entry(rent_content, font=('Helvetica', 11), width=15)
        self.deposit_entry.grid(row=0, column=3, padx=10, pady=10)
        if self.rent_data['security_deposit'] > 0:
            self.deposit_entry.insert(0, str(self.rent_data['security_deposit']))
        
        tk.Label(rent_content, text="Maintenance (₹):", bg='white').grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)
        self.maintenance_entry = tk.Entry(rent_content, font=('Helvetica', 11), width=15)
        self.maintenance_entry.grid(row=1, column=1, padx=10, pady=10)
        if self.rent_data['maintenance'] > 0:
            self.maintenance_entry.insert(0, str(self.rent_data['maintenance']))
        
        period_card = self.create_card(basic_tab, "📅 Payment Period")
        period_card.pack(fill=tk.X, pady=10, padx=10)
        
        period_content = tk.Frame(period_card, bg='white')
        period_content.pack(pady=10, padx=10)
        
        tk.Label(period_content, text="Month:", bg='white').grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        months = ['January', 'February', 'March', 'April', 'May', 'June',
                 'July', 'August', 'September', 'October', 'November', 'December']
        self.month_combo = ttk.Combobox(period_content, values=months, state="readonly", width=15)
        self.month_combo.grid(row=0, column=1, padx=10, pady=10)
        self.month_combo.current(datetime.datetime.now().month - 1)
        
        tk.Label(period_content, text="Year:", bg='white').grid(row=0, column=2, sticky=tk.W, padx=10, pady=10)
        current_year = datetime.datetime.now().year
        years = [str(current_year - 1), str(current_year), str(current_year + 1)]
        self.year_combo = ttk.Combobox(period_content, values=years, state="readonly", width=10)
        self.year_combo.grid(row=0, column=3, padx=10, pady=10)
        self.year_combo.current(1)
        
        calc_btn = tk.Button(basic_tab, text="💰 Calculate Rent", command=self.calculate_rent,
                            bg=self.colors['accent'], fg='white', font=('Helvetica', 12, 'bold'),
                            padx=30, pady=10)
        calc_btn.pack(pady=20)
    
    def setup_tenants_tab(self):
        tenants_tab = tk.Frame(self.notebook, bg=self.colors['background'])
        self.notebook.add(tenants_tab, text="👥 Tenants & Split")
        
        split_card = self.create_card(tenants_tab, "⚖️ Split Type")
        split_card.pack(fill=tk.X, pady=10, padx=10)
        
        split_content = tk.Frame(split_card, bg='white')
        split_content.pack(pady=10, padx=10)
        
        self.split_var = tk.StringVar(value="equal")
        
        tk.Radiobutton(split_content, text="Equal Split", variable=self.split_var, 
                      value="equal", bg='white', command=self.update_split_type).grid(row=0, column=0, padx=20, pady=10)
        tk.Radiobutton(split_content, text="By Room Size", variable=self.split_var, 
                      value="room", bg='white', command=self.update_split_type).grid(row=0, column=1, padx=20, pady=10)
        tk.Radiobutton(split_content, text="Custom Percentage", variable=self.split_var, 
                      value="custom", bg='white', command=self.update_split_type).grid(row=0, column=2, padx=20, pady=10)
        
        tenants_list_card = self.create_card(tenants_tab, "👤 Tenants List")
        tenants_list_card.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)
        
        columns = ('Name', 'Room Size (sq ft)', 'Percentage', 'Share (₹)')
        self.tenants_tree = ttk.Treeview(tenants_list_card, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.tenants_tree.heading(col, text=col)
            self.tenants_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(tenants_list_card, orient=tk.VERTICAL, command=self.tenants_tree.yview)
        self.tenants_tree.configure(yscrollcommand=scrollbar.set)
        
        self.tenants_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        controls_frame = tk.Frame(tenants_list_card, bg='white')
        controls_frame.pack(fill=tk.X, pady=10, padx=10)
        
        tk.Label(controls_frame, text="Name:", bg='white').pack(side=tk.LEFT, padx=5)
        self.tenant_name_entry = tk.Entry(controls_frame, width=15)
        self.tenant_name_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(controls_frame, text="Room Size:", bg='white').pack(side=tk.LEFT, padx=5)
        self.room_size_entry = tk.Entry(controls_frame, width=10)
        self.room_size_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(controls_frame, text="Percentage:", bg='white').pack(side=tk.LEFT, padx=5)
        self.percentage_entry = tk.Entry(controls_frame, width=10)
        self.percentage_entry.pack(side=tk.LEFT, padx=5)
        
        add_btn = tk.Button(controls_frame, text="➕ Add", command=self.add_tenant,
                           bg=self.colors['primary'], fg='white')
        add_btn.pack(side=tk.LEFT, padx=10)
        
        del_btn = tk.Button(controls_frame, text="🗑️ Remove", command=self.remove_tenant,
                           bg=self.colors['danger'], fg='white')
        del_btn.pack(side=tk.LEFT, padx=5)
        
        self.load_tenants_to_tree()
    
    def setup_utilities_tab(self):
        utilities_tab = tk.Frame(self.notebook, bg=self.colors['background'])
        self.notebook.add(utilities_tab, text="💡 Utilities")
        
        utilities_card = self.create_card(utilities_tab, "🔌 Utilities Breakdown")
        utilities_card.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)
        
        columns = ('Utility', 'Amount (₹)', 'Split Method', 'Notes')
        self.utilities_tree = ttk.Treeview(utilities_card, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.utilities_tree.heading(col, text=col)
            self.utilities_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(utilities_card, orient=tk.VERTICAL, command=self.utilities_tree.yview)
        self.utilities_tree.configure(yscrollcommand=scrollbar.set)
        
        self.utilities_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        controls_frame = tk.Frame(utilities_card, bg='white')
        controls_frame.pack(fill=tk.X, pady=10, padx=10)
        
        tk.Label(controls_frame, text="Utility:", bg='white').pack(side=tk.LEFT, padx=5)
        self.util_name_entry = tk.Entry(controls_frame, width=15)
        self.util_name_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(controls_frame, text="Amount:", bg='white').pack(side=tk.LEFT, padx=5)
        self.util_amount_entry = tk.Entry(controls_frame, width=10)
        self.util_amount_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(controls_frame, text="Split:", bg='white').pack(side=tk.LEFT, padx=5)
        self.util_split_combo = ttk.Combobox(controls_frame, 
                                           values=['Equal', 'By Usage', 'Custom'], 
                                           state="readonly", width=10)
        self.util_split_combo.pack(side=tk.LEFT, padx=5)
        self.util_split_combo.current(0)
        
        tk.Label(controls_frame, text="Notes:", bg='white').pack(side=tk.LEFT, padx=5)
        self.util_notes_entry = tk.Entry(controls_frame, width=20)
        self.util_notes_entry.pack(side=tk.LEFT, padx=5)
        
        add_util_btn = tk.Button(controls_frame, text="➕ Add", command=self.add_utility,
                                bg=self.colors['primary'], fg='white')
        add_util_btn.pack(side=tk.LEFT, padx=10)
        
        del_util_btn = tk.Button(controls_frame, text="🗑️ Remove", command=self.remove_utility,
                                bg=self.colors['danger'], fg='white')
        del_util_btn.pack(side=tk.LEFT, padx=5)
        
        common_frame = tk.Frame(utilities_card, bg='white')
        common_frame.pack(fill=tk.X, pady=10, padx=10)
        
        tk.Label(common_frame, text="Quick Add:", bg='white', font=('Helvetica', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        
        common_utilities = [
            ("⚡ Electricity", 1500),
            ("💧 Water", 500),
            ("🌐 Internet", 1000),
            ("🗑️ Gas", 400),
            ("📺 Cable TV", 300)
        ]
        
        for util_name, util_amount in common_utilities:
            btn = tk.Button(common_frame, text=f"{util_name} (₹{util_amount})", 
                           command=lambda n=util_name, a=util_amount: self.quick_add_utility(n, a),
                           bg=self.colors['light'])
            btn.pack(side=tk.LEFT, padx=2)
        
        self.load_utilities_to_tree()
    
    def setup_results_tab(self):
        results_tab = tk.Frame(self.notebook, bg=self.colors['background'])
        self.notebook.add(results_tab, text="📊 Results & History")
        
        results_frame = tk.Frame(results_tab, bg=self.colors['card'], relief=tk.RAISED, bd=2)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, height=20, 
                                                     font=('Courier', 10),
                                                     bg='white', fg=self.colors['dark'])
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        button_frame = tk.Frame(results_tab, bg=self.colors['background'])
        button_frame.pack(fill=tk.X, pady=10, padx=10)
        
        tk.Button(button_frame, text="📋 Copy to Clipboard", command=self.copy_to_clipboard,
                 bg=self.colors['primary'], fg='white').pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="💾 Save Calculation", command=self.save_calculation,
                 bg=self.colors['success'], fg='white').pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="📄 Generate Report", command=self.generate_report,
                 bg=self.colors['accent'], fg='white').pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="🔄 Clear All", command=self.clear_all,
                 bg=self.colors['danger'], fg='white').pack(side=tk.LEFT, padx=5)
    
    def create_card(self, parent, title):
        card = tk.Frame(parent, bg=self.colors['card'], relief=tk.RAISED, bd=2)
        
        title_label = tk.Label(card, text=title, font=('Helvetica', 12, 'bold'),
                              bg=self.colors['card'], fg=self.colors['dark'])
        title_label.pack(pady=10)
        
        return card
    
    def update_split_type(self):
        split_type = self.split_var.get()
        if split_type == "equal":
            self.percentage_entry.config(state='disabled')
            self.room_size_entry.config(state='disabled')
        elif split_type == "room":
            self.percentage_entry.config(state='disabled')
            self.room_size_entry.config(state='normal')
        else: 
            self.percentage_entry.config(state='normal')
            self.room_size_entry.config(state='disabled')
    
    def add_tenant(self):
        name = self.tenant_name_entry.get().strip()
        
        if not name:
            messagebox.showerror("Error", "Please enter tenant name!")
            return
        
        split_type = self.split_var.get()
        
        if split_type == "room":
            try:
                room_size = float(self.room_size_entry.get())
                if room_size <= 0:
                    raise ValueError
            except:
                messagebox.showerror("Error", "Please enter valid room size!")
                return
        
        if split_type == "custom":
            try:
                percentage = float(self.percentage_entry.get())
                if percentage <= 0 or percentage > 100:
                    raise ValueError
            except:
                messagebox.showerror("Error", "Please enter valid percentage (0-100)!")
                return
        
        tenant_data = {'name': name}
        
        if split_type == "room":
            tenant_data['room_size'] = room_size
            tenant_data['percentage'] = 0
        elif split_type == "custom":
            tenant_data['percentage'] = percentage
            tenant_data['room_size'] = 0
        else:  
            tenant_data['percentage'] = 0
            tenant_data['room_size'] = 0
        
        if split_type == "room":
            self.tenants_tree.insert('', 'end', values=(name, room_size, 'Auto', '₹0'))
        elif split_type == "custom":
            self.tenants_tree.insert('', 'end', values=(name, 'N/A', f'{percentage}%', '₹0'))
        else: 
            self.tenants_tree.insert('', 'end', values=(name, 'N/A', 'Equal', '₹0'))
        
        self.rent_data['tenants'].append(tenant_data)
        
        self.tenant_name_entry.delete(0, tk.END)
        self.room_size_entry.delete(0, tk.END)
        self.percentage_entry.delete(0, tk.END)
    
    def remove_tenant(self):
        selected = self.tenants_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a tenant to remove!")
            return
        
        if messagebox.askyesno("Confirm", "Remove selected tenant?"):
            for item in selected:
                values = self.tenants_tree.item(item)['values']
                name = values[0]
                
                self.rent_data['tenants'] = [t for t in self.rent_data['tenants'] if t['name'] != name]
                self.tenants_tree.delete(item)
    
    def add_utility(self):
        name = self.util_name_entry.get().strip()
        
        if not name:
            messagebox.showerror("Error", "Please enter utility name!")
            return
        
        try:
            amount = float(self.util_amount_entry.get())
            if amount <= 0:
                raise ValueError
        except:
            messagebox.showerror("Error", "Please enter valid amount!")
            return
        
        split_method = self.util_split_combo.get()
        notes = self.util_notes_entry.get().strip()
    
        self.utilities_tree.insert('', 'end', values=(name, f'₹{amount:,.2f}', split_method, notes))
        
        if 'utilities' not in self.rent_data:
            self.rent_data['utilities'] = {}
        
        self.rent_data['utilities'][name] = {
            'amount': amount,
            'split_method': split_method,
            'notes': notes
        }
        
        self.util_name_entry.delete(0, tk.END)
        self.util_amount_entry.delete(0, tk.END)
        self.util_notes_entry.delete(0, tk.END)
    
    def quick_add_utility(self, name, amount):
        self.util_name_entry.delete(0, tk.END)
        self.util_amount_entry.delete(0, tk.END)
        self.util_notes_entry.delete(0, tk.END)
        
        self.util_name_entry.insert(0, name)
        self.util_amount_entry.insert(0, str(amount))
        self.add_utility()
    
    def remove_utility(self):
        selected = self.utilities_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a utility to remove!")
            return
        
        if messagebox.askyesno("Confirm", "Remove selected utility?"):
            for item in selected:
                values = self.utilities_tree.item(item)['values']
                name = values[0]
                
                if name in self.rent_data.get('utilities', {}):
                    del self.rent_data['utilities'][name]
                
                self.utilities_tree.delete(item)
    
    def calculate_rent(self):
        try:
            rent_amount = float(self.rent_entry.get()) if self.rent_entry.get() else 0
            security_deposit = float(self.deposit_entry.get()) if self.deposit_entry.get() else 0
            maintenance = float(self.maintenance_entry.get()) if self.maintenance_entry.get() else 0
            
            if rent_amount <= 0:
                messagebox.showerror("Error", "Please enter valid rent amount!")
                return
            
            self.rent_data['rent_amount'] = rent_amount
            self.rent_data['security_deposit'] = security_deposit
            self.rent_data['maintenance'] = maintenance
            self.rent_data['split_type'] = self.split_var.get()
            
            utilities_total = sum(util['amount'] for util in self.rent_data.get('utilities', {}).values())
            
            total_monthly = rent_amount + maintenance + utilities_total
            split_type = self.split_var.get()
            tenants = self.rent_data['tenants']
            
            if not tenants:
                messagebox.showerror("Error", "Please add at least one tenant!")
                return
            
            results = []
            results.append("=" * 60)
            results.append(f"🏠 RENT CALCULATION FOR {self.month_combo.get().upper()} {self.year_combo.get()}")
            results.append("=" * 60)
            results.append("")
            results.append(f"📋 BASIC INFORMATION")
            results.append("-" * 40)
            results.append(f"Monthly Rent:           ₹{rent_amount:,.2f}")
            results.append(f"Maintenance:            ₹{maintenance:,.2f}")
            results.append(f"Security Deposit:       ₹{security_deposit:,.2f}")
            results.append("")
            
            if utilities_total > 0:
                results.append(f"💡 UTILITIES BREAKDOWN (Total: ₹{utilities_total:,.2f})")
                results.append("-" * 40)
                for name, util in self.rent_data.get('utilities', {}).items():
                    results.append(f"{name:20} ₹{util['amount']:,.2f}  ({util['split_method']})")
                results.append("")
            
            results.append(f"💰 MONTHLY TOTAL: ₹{total_monthly:,.2f}")
            results.append("")
            
            if split_type == "equal":
                results.append(f"⚖️ SPLIT TYPE: Equal ({len(tenants)} tenants)")
                results.append("-" * 40)
                share_per_tenant = total_monthly / len(tenants)
                for i, tenant in enumerate(tenants):
                    results.append(f"{i+1}. {tenant['name']:15} ₹{share_per_tenant:,.2f}")
                
                    items = self.tenants_tree.get_children()
                    if i < len(items):
                        self.tenants_tree.item(items[i], values=(
                            tenant['name'], 'N/A', 'Equal', f'₹{share_per_tenant:,.2f}'
                        ))
            
            elif split_type == "room":
                results.append(f"⚖️ SPLIT TYPE: By Room Size")
                results.append("-" * 40)
                
                total_room_size = sum(t.get('room_size', 0) for t in tenants)
                if total_room_size == 0:
                    messagebox.showerror("Error", "Please add room sizes for all tenants!")
                    return
                
                for i, tenant in enumerate(tenants):
                    room_size = tenant.get('room_size', 0)
                    percentage = (room_size / total_room_size) * 100
                    share = total_monthly * (room_size / total_room_size)
                    
                    results.append(f"{i+1}. {tenant['name']:15} {room_size:,.0f} sq ft ({percentage:.1f}%) = ₹{share:,.2f}")
                    
                    items = self.tenants_tree.get_children()
                    if i < len(items):
                        self.tenants_tree.item(items[i], values=(
                            tenant['name'], f'{room_size:,.0f} sq ft', f'{percentage:.1f}%', f'₹{share:,.2f}'
                        ))
            
            elif split_type == "custom":
                results.append(f"⚖️ SPLIT TYPE: Custom Percentage")
                results.append("-" * 40)
                
                total_percentage = sum(t.get('percentage', 0) for t in tenants)
                if abs(total_percentage - 100) > 0.1:
                    messagebox.showerror("Error", f"Total percentage must be 100% (Current: {total_percentage:.1f}%)")
                    return
                
                for i, tenant in enumerate(tenants):
                    percentage = tenant.get('percentage', 0)
                    share = total_monthly * (percentage / 100)
                    
                    results.append(f"{i+1}. {tenant['name']:15} {percentage:.1f}% = ₹{share:,.2f}")
                    
                    items = self.tenants_tree.get_children()
                    if i < len(items):
                        self.tenants_tree.item(items[i], values=(
                            tenant['name'], 'N/A', f'{percentage:.1f}%', f'₹{share:,.2f}'
                        ))
            
            results.append("")
            results.append(f"🏦 SECURITY DEPOSIT PER TENANT: ₹{security_deposit/len(tenants):,.2f}")
            results.append("")
            results.append("💡 TIPS:")
            results.append("- Split utilities equally or based on usage")
            results.append("- Keep records of all payments")
            results.append("- Set payment deadlines")
            results.append("=" * 60)
            
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(1.0, '\n'.join(results))
            
            self.notebook.select(3)  
            
        except ValueError as e:
            messagebox.showerror("Error", "Please enter valid numbers in all fields!")
    
    def copy_to_clipboard(self):
        text = self.results_text.get(1.0, tk.END)
        if text.strip():
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            messagebox.showinfo("Success", "Results copied to clipboard!")
    
    def save_calculation(self):
        text = self.results_text.get(1.0, tk.END)
        if not text.strip():
            messagebox.showwarning("Warning", "No calculation to save!")
            return
        
        month = self.month_combo.get()
        year = self.year_combo.get()
        
        filename = f"rent_calculation_{month}_{year}.txt"
        
        try:
            with open(filename, 'w') as f:
                f.write(text)
            messagebox.showinfo("Success", f"Calculation saved to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {str(e)}")
    
    def generate_report(self):
        if not self.rent_data['tenants']:
            messagebox.showwarning("Warning", "No data to generate report!")
            return
        
        report = []
        report.append("=" * 70)
        report.append("📊 RENT PAYMENT REPORT")
        report.append("=" * 70)
        report.append("")
        report.append(f"Period: {self.month_combo.get()} {self.year_combo.get()}")
        report.append(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append("")
        report.append("📋 PAYMENT DETAILS")
        report.append("-" * 70)
        
        total_rent = self.rent_data.get('rent_amount', 0)
        total_maintenance = self.rent_data.get('maintenance', 0)
        total_utilities = sum(util['amount'] for util in self.rent_data.get('utilities', {}).values())
        total_monthly = total_rent + total_maintenance + total_utilities
        
        report.append(f"Monthly Rent:           ₹{total_rent:,.2f}")
        report.append(f"Maintenance:            ₹{total_maintenance:,.2f}")
        report.append(f"Utilities:              ₹{total_utilities:,.2f}")
        report.append("-" * 70)
        report.append(f"TOTAL MONTHLY:          ₹{total_monthly:,.2f}")
        report.append("")
        
        report.append("👥 TENANT PAYMENT BREAKDOWN")
        report.append("-" * 70)
        
        tenants = self.rent_data['tenants']
        split_type = self.rent_data.get('split_type', 'equal')
        
        if split_type == "equal":
            share_per_tenant = total_monthly / len(tenants)
            for i, tenant in enumerate(tenants):
                report.append(f"{i+1}. {tenant['name']:20} ₹{share_per_tenant:,.2f}")
        
        elif split_type == "room":
            total_room_size = sum(t.get('room_size', 0) for t in tenants)
            for i, tenant in enumerate(tenants):
                room_size = tenant.get('room_size', 0)
                percentage = (room_size / total_room_size) * 100
                share = total_monthly * (room_size / total_room_size)
                report.append(f"{i+1}. {tenant['name']:20} {room_size:,.0f} sq ft ({percentage:.1f}%) = ₹{share:,.2f}")
        
        elif split_type == "custom":
            for i, tenant in enumerate(tenants):
                percentage = tenant.get('percentage', 0)
                share = total_monthly * (percentage / 100)
                report.append(f"{i+1}. {tenant['name']:20} {percentage:.1f}% = ₹{share:,.2f}")
        
        report.append("")
        report.append("💡 UTILITIES DETAILS")
        report.append("-" * 70)
        
        if self.rent_data.get('utilities'):
            for name, util in self.rent_data['utilities'].items():
                report.append(f"{name:25} ₹{util['amount']:,.2f} ({util['split_method']})")
        else:
            report.append("No utilities added")
        
        report.append("")
        report.append("📋 PAYMENT INSTRUCTIONS")
        report.append("-" * 70)
        report.append("1. Please pay your share by the 5th of each month")
        report.append("2. Use UPI, Bank Transfer, or Cash")
        report.append("3. Keep transaction ID for reference")
        report.append("4. Notify if payment will be delayed")
        report.append("")
        report.append("=" * 70)
        
        report_window = tk.Toplevel(self.root)
        report_window.title("Rent Payment Report")
        report_window.geometry("800x600")
        
        text_widget = scrolledtext.ScrolledText(report_window, font=('Courier', 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(1.0, '\n'.join(report))
        text_widget.config(state='disabled')
       
        save_btn = tk.Button(report_window, text="💾 Save Report", 
                            command=lambda: self.save_report('\n'.join(report)),
                            bg=self.colors['accent'], fg='white')
        save_btn.pack(pady=10)
    
    def save_report(self, report_text):
        filename = f"rent_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        try:
            with open(filename, 'w') as f:
                f.write(report_text)
            messagebox.showinfo("Success", f"Report saved to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {str(e)}")
    
    def clear_all(self):
        if messagebox.askyesno("Confirm", "Clear all data? This cannot be undone!"):
            self.rent_entry.delete(0, tk.END)
            self.deposit_entry.delete(0, tk.END)
            self.maintenance_entry.delete(0, tk.END)
            for item in self.tenants_tree.get_children():
                self.tenants_tree.delete(item)
            
            for item in self.utilities_tree.get_children():
                self.utilities_tree.delete(item)
            
            self.results_text.delete(1.0, tk.END)
        
            self.rent_data = {
                'rent_amount': 0,
                'utilities': {},
                'tenants': [],
                'split_type': 'equal',
                'security_deposit': 0,
                'maintenance': 0
            }
            
            self.save_data()
            
            messagebox.showinfo("Cleared", "All data has been cleared!")
    
    def load_tenants_to_tree(self):
        for tenant in self.rent_data['tenants']:
            name = tenant.get('name', '')
            room_size = tenant.get('room_size', 0)
            percentage = tenant.get('percentage', 0)
            
            if room_size > 0:
                self.tenants_tree.insert('', 'end', values=(name, f'{room_size} sq ft', 'Auto', '₹0'))
            elif percentage > 0:
                self.tenants_tree.insert('', 'end', values=(name, 'N/A', f'{percentage}%', '₹0'))
            else:
                self.tenants_tree.insert('', 'end', values=(name, 'N/A', 'Equal', '₹0'))
    
    def load_utilities_to_tree(self):
        for name, util in self.rent_data.get('utilities', {}).items():
            amount = util.get('amount', 0)
            split_method = util.get('split_method', 'Equal')
            notes = util.get('notes', '')
            self.utilities_tree.insert('', 'end', values=(name, f'₹{amount:,.2f}', split_method, notes))
    
    def save_data(self):
        try:
            with open('rent_calculator_data.json', 'w') as f:
                json.dump(self.rent_data, f, indent=4)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def load_data(self):
        try:
            if os.path.exists('rent_calculator_data.json'):
                with open('rent_calculator_data.json', 'r') as f:
                    self.rent_data = json.load(f)
        except Exception as e:
            print(f"Error loading data: {e}")

def main():
    root = tk.Tk()
    app = RentCalculator(root)
    root.mainloop()

if __name__ == "__main__":
    main()