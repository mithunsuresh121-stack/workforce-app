const { Client } = require('pg');
require('dotenv').config();

const client = new Client({
  host: process.env.DB_HOST || 'localhost',
  port: process.env.DB_PORT || 5432,
  user: process.env.DB_USER || 'mithunsuresh',
  password: process.env.DB_PASSWORD || '',
  database: process.env.DB_NAME || 'workforce'
});

client.connect()
  .then(() => {
    console.log('Connected to PostgreSQL database');

    // Check users table
    return client.query('SELECT id, email, role, company_id FROM users LIMIT 10');
  })
  .then(result => {
    console.log('=== Users Table (first 10) ===');
    result.rows.forEach(row => {
      console.log(row);
    });

    // Check task status enum
    return client.query("SELECT enumlabel FROM pg_enum e JOIN pg_type t ON e.enumtypid=t.oid WHERE t.typname='taskstatus'");
  })
  .then(result => {
    console.log('\n=== TaskStatus Enum ===');
    console.log(result.rows.map(r => r.enumlabel));

    // Check task priority enum
    return client.query("SELECT enumlabel FROM pg_enum e JOIN pg_type t ON e.enumtypid=t.oid WHERE t.typname='taskpriority'");
  })
  .then(result => {
    console.log('\n=== TaskPriority Enum ===');
    console.log(result.rows.map(r => r.enumlabel));

    client.end();
  })
  .catch(err => {
    console.error('Error:', err);
    client.end();
  });
