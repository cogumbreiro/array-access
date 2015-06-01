use std::collections::HashMap;
use std::vec::Vec;
use std::cmp::Ordering;
use std::cmp;

#[derive(Debug,PartialEq,Clone)]
struct Atom {level : i32, constant : i32, variable : bool}

impl Atom {
    fn level_cmp(&self, other:&Atom) -> Ordering {
        return self.level.cmp(&(other.level))
    }
    // Add two atoms, if they are at the same level
    fn add(&self, other:&Atom) -> Option<Atom> {
        if self.level == other.level {
            Some(Atom{level: self.level,
                    constant : self.constant + other.constant,
                    variable : self.variable || other.variable})
        } else {
            None
        }
    }
    
    fn mul(&self, other:&Atom) -> Atom {
        return Atom {
            level: cmp::max(other.level, self.level),
            constant: self.constant * other.constant,
            variable: self.variable || other.variable
        }
    }
}

#[test]
fn test_mul() {
    assert_eq!(
        (&Atom{level:0, constant: 2, variable: true}).mul(
            &Atom{level:1, constant: 3, variable: false}
        ), Atom{level:1, constant: 6, variable: true});
}

#[derive(Debug,PartialEq)]
enum Expr {
    Int(i32),
    Var(String),
    Add(Box<Expr>, Box<Expr>)
}

struct Interpreter {
    env:HashMap<String, i32>
}

impl Interpreter {
    fn new() -> Interpreter {
        let mut env = HashMap::new();
        env.insert("i".to_string(), 1);
        env.insert("j".to_string(), 2);
        env.insert("k".to_string(), 3);
        Interpreter {
            env: env,
        }
    }

    fn get_level(&self, atom:&str) -> i32 {
        match self.env.get(atom) {
            Some(idx) => *idx,
            None => 0
        }
    }

    fn get_var(&self, name:&str) -> Atom {
        let lvl = self.get_level(name);
        if lvl == 0 {
            return Atom{level:lvl, constant:0, variable:true}
        }
        Atom{level:lvl, constant:1, variable:false}
    }
    
    fn get_int(&self, value:i32) -> Atom {
        Atom{level:0, constant:value, variable:false}
    }
    
    fn flatten(&self, expr:Expr) -> Vec<Atom> {
        let mut result : Vec<Atom> = vec!();
        match expr {
            Expr::Add(lhs, rhs) => {
                result.extend(self.flatten(*lhs).into_iter());
                result.extend(self.flatten(*rhs).into_iter());
            },
            Expr::Int(a) => result.push(self.get_int(a)),
            Expr::Var(a) => result.push(self.get_var(&a)),
        }
        result
    }
    
    fn eval(&self, expr:Expr) -> Vec<Atom> {
        let mut atoms = self.flatten(expr);
        atoms.sort_by(|a,b| a.level_cmp(b));
        let mut result: Vec<Atom> = vec![];
        for rhs in atoms {
            // we add expressions to the end,
            // but when adding an element, we try to add it to the
            // last element instead
            let mut failed_add = true;
            if let Some(lhs) = result.last_mut() {
                if let Some(sum) = lhs.add(&rhs) {
                    // if given and last can be added, then
                    // we update the last to the sum
                    *lhs = sum;
                    failed_add = false;
                }
            }
            if failed_add {
                result.push(rhs);
            }
        }
        result
    }
}

#[test]
fn test_get_level() -> () {
    let x = Interpreter::new();
    assert_eq!(x.get_level("x"), 0);
    assert_eq!(x.get_level("i"), 1);
    assert_eq!(x.get_level("j"), 2);
    assert_eq!(x.get_level("k"), 3);
}
#[test]
fn test_create_var_const() -> () {
    let x = Interpreter::new();
    assert_eq!(Atom{level:0, constant:1, variable:false}, x.get_int(1));
    assert_eq!(Atom{level:0, constant:0, variable:true}, x.get_var("x"));
    assert_eq!(Atom{level:1, constant:1, variable:false}, x.get_var("i"));
    assert_eq!(Atom{level:2, constant:1, variable:false}, x.get_var("j"));
    assert_eq!(Atom{level:3, constant:1, variable:false}, x.get_var("k"));
}

#[test]
fn test_eval() -> () {
    let add = |x:Expr, y:Expr| {Expr::Add(Box::new(x), Box::new(y))};
    let run = Interpreter::new();
    assert_eq!(run.eval(Expr::Int(1)),
        vec![Atom{level:0, constant:1, variable:false}]);
        
    assert_eq!(run.eval(add(Expr::Int(1), Expr::Int(1))),
        vec![Atom{level:0, constant:2, variable:false}]);
        
    assert_eq!(run.eval(add(Expr::Int(1), Expr::Var("x".to_string()))),
        vec![Atom{level:0, constant:1, variable:true}]);
        
    assert_eq!(run.eval(add(add(Expr::Int(1), Expr::Var("x".to_string())), Expr::Int(2))),
        vec![Atom{level:0, constant:3, variable:true}]);
        
    assert_eq!(run.eval(add(add(Expr::Int(1), Expr::Var("j".to_string())), Expr::Var("i".to_string()))),
        vec![Atom{level:0, constant:1, variable:false},
             Atom{level:1, constant:1, variable:false},
             Atom{level:2, constant:1, variable:false}]);
}


