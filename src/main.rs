extern crate rustc_serialize;
#[macro_use] extern crate maplit;

use std::collections::HashMap;
use std::vec::Vec;
use std::cmp::Ordering;
use std::cmp;
use rustc_serialize::json::{Json, ToJson};

type Num = i64;

#[derive(Debug, PartialEq, Clone)]
struct Atom {level : i32, constant : Num, variable : bool}

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
    // (2 + a) * 3 * i = (6 + 3 * a) * i = (6 + a) * i
    assert_eq!(
        (&Atom{level:0, constant: 2, variable: true}).mul(
            &Atom{level:1, constant: 3, variable: false}
        ), Atom{level:1, constant: 6, variable: true});
    // (2 + a)*i * 3*j = ( 6 + true ) j
    assert_eq!(
        (&Atom{level:1, constant: 2, variable: true}).mul(
            &Atom{level:2, constant: 3, variable: false}
        ), Atom{level:2, constant: 6, variable: true});

}

#[derive(Debug,PartialEq, Clone)]
enum Expr {
    Num(Num),
    Var(String),
    UMinus(Box<Expr>),
    Minus(Box<Expr>, Box<Expr>),
    Mul(Box<Expr>, Box<Expr>),
    Add(Box<Expr>, Box<Expr>)
}

type Env = HashMap<String, i32>;

struct Interpreter {
    env:Env
}

impl Interpreter {
    fn new(env:&Env) -> Interpreter {
        Interpreter {env: env.clone(), }
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
    
    fn get_num(&self, value:Num) -> Atom {
        Atom{level:0, constant:value, variable:false}
    }
    
    fn normalize(&self, expr:&Expr) -> Vec<Atom> {
        let mut result : Vec<Atom> = vec!();
        match expr {
            &Expr::Mul(ref lhs, ref rhs) => {
                let lhs_sum = self.normalize(&*lhs);
                let rhs_sum = self.normalize(&*rhs);
                for x in &lhs_sum {
                    for y in &rhs_sum {
                        result.push(x.mul(&y));
                    }
                }
            }
            &Expr::Add(ref lhs, ref rhs) => {
                result.extend(self.normalize(&*lhs).into_iter());
                result.extend(self.normalize(&*rhs).into_iter());
            },
            &Expr::UMinus(ref negexpr) => {
                let negexpr_copy = (**negexpr).clone();
                let simpl = Expr::Mul(Box::new(Expr::Num(-1)), Box::new(negexpr_copy));
                result.extend(self.normalize(&simpl).into_iter());
            },
            &Expr::Minus(ref lhs, ref rhs) => {
                let rhs_copy = Box::new((**rhs).clone());
                let lhs_copy = Box::new((**lhs).clone());
                let simpl = Expr::Add(lhs_copy, Box::new(Expr::UMinus(rhs_copy)));
                result.extend(self.normalize(&simpl).into_iter());
            }
            &Expr::Num(ref a) => result.push(self.get_num(*a)),
            &Expr::Var(ref a) => result.push(self.get_var(a)),
        }
        result
    }
    
    fn eval(&self, expr:&Expr) -> Vec<Atom> {
        let mut atoms = self.normalize(expr);
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

#[cfg(test)]
fn for_ijk() -> Interpreter {
    Interpreter::new(
        &hashmap!{
            "i".to_string() => 1,
            "j".to_string() => 2,
            "k".to_string() => 3
        }
    )
}

#[test]
fn test_get_level() -> () {
    let x = for_ijk();
    
    assert_eq!(x.get_level("x"), 0);
    assert_eq!(x.get_level("i"), 1);
    assert_eq!(x.get_level("j"), 2);
    assert_eq!(x.get_level("k"), 3);
}
#[test]
fn test_create_var_const() -> () {
    let x = for_ijk();
    
    assert_eq!(Atom{level:0, constant:1, variable:false}, x.get_num(1));
    assert_eq!(Atom{level:0, constant:0, variable:true}, x.get_var("x"));
    assert_eq!(Atom{level:1, constant:1, variable:false}, x.get_var("i"));
    assert_eq!(Atom{level:2, constant:1, variable:false}, x.get_var("j"));
    assert_eq!(Atom{level:3, constant:1, variable:false}, x.get_var("k"));
}

#[test]
fn test_eval() -> () {
    let add = |x:Expr, y:Expr| {Expr::Add(Box::new(x), Box::new(y))};
    let run = for_ijk();
    assert_eq!(run.eval(&Expr::Num(1)),
        vec![Atom{level:0, constant:1, variable:false}]);
        
    assert_eq!(run.eval(&add(Expr::Num(1), Expr::Num(1))),
        vec![Atom{level:0, constant:2, variable:false}]);
        
    assert_eq!(run.eval(&add(Expr::Num(1), Expr::Var("x".to_string()))),
        vec![Atom{level:0, constant:1, variable:true}]);
        
    assert_eq!(run.eval(&add(add(Expr::Num(1), Expr::Var("x".to_string())), Expr::Num(2))),
        vec![Atom{level:0, constant:3, variable:true}]);
        
    assert_eq!(run.eval(&add(add(Expr::Num(1), Expr::Var("j".to_string())), Expr::Var("i".to_string()))),
        vec![Atom{level:0, constant:1, variable:false},
             Atom{level:1, constant:1, variable:false},
             Atom{level:2, constant:1, variable:false}]);
}

#[derive(Debug, PartialEq)]
enum ExprParseError {
    Add,
    UMinus,
    Minus,
    Mul,
    UnsupportedType,
    Unknown
}

impl Expr {
    fn from_json(data:&Json) -> Result<Expr,ExprParseError> {
        match data {
            &Json::Object(ref obj) => {
                // expression
                if let Some(&Json::String(ref op)) = obj.get("op") {
                    if let Some(&Json::Array(ref operands)) = obj.get("args") {
                        if *op == "+" && 1 <= operands.len() && operands.len() <= 2 {
                            if operands.len() == 1 {
                                return Expr::from_json(&operands[0])
                            }
                            let op1 = Expr::from_json(&operands[0]);
                            let op2 = Expr::from_json(&operands[1]);
                            if let (Ok(lhs), Ok(rhs)) = (op1, op2) {
                                return Ok(Expr::Add(Box::new(lhs), Box::new(rhs)))
                            }
                            return Err(ExprParseError::Add)
                        } else if *op == "-" && 1 <= operands.len() && operands.len() <= 2  {
                            if operands.len() == 1 {
                                return Expr::from_json(&operands[0]).
                                    or_else(|err| Err(ExprParseError::UMinus)).
                                    and_then(|uminus| Ok(Expr::UMinus(Box::new(uminus))));
                            }
                            
                            let op1 = Expr::from_json(&operands[0]);
                            let op2 = Expr::from_json(&operands[1]);
                            if let (Ok(lhs), Ok(rhs)) = (op1, op2) {
                                return Ok(Expr::Minus(Box::new(lhs), Box::new(rhs)))
                            }
                            return Err(ExprParseError::Minus)
                        } else if *op == "*" && operands.len() == 2  {
                            let op1 = Expr::from_json(&operands[0]);
                            let op2 = Expr::from_json(&operands[1]);
                            if let (Ok(lhs), Ok(rhs)) = (op1, op2) {
                                return Ok(Expr::Mul(Box::new(lhs), Box::new(rhs)))
                            }
                            return Err(ExprParseError::Mul)
                        }
                    }
                }
            }
            
            &Json::String(ref name) => {
                // variable
                return Ok(Expr::Var(name.clone()))
            }
            
            &Json::I64(ref num) => {
                // number
                return Ok(Expr::Num(*num))
            }

            &Json::U64(ref num) => {
                // number
                return Ok(Expr::Num(*num as i64))
            }
            _ => {return Err(ExprParseError::UnsupportedType)}
        }
        Err(ExprParseError::Unknown)
    }
}

#[test]
fn test_json_to_expr () {
    if let Ok(x) = Json::from_str("\"i\"") {
        assert_eq!(Expr::from_json(&x), Ok(Expr::Var("i".to_string())));
    } else { assert!(false); }

    if let Ok(x) = Json::from_str("1") {
        println!("{}", x);
        assert_eq!(Expr::from_json(&x), Ok(Expr::Num(1)));
    } else {assert!(false); }

    if let Ok(x) = Json::from_str("{\"op\": \"+\", \"args\": [1,\"i\"]}") {
        assert_eq!(Expr::from_json(&x), Ok(Expr::Add(Box::new(Expr::Num(1)), Box::new(Expr::Var("i".to_string())))));
    } else {assert!(false); }
    
}

impl ToJson for Atom {
    fn to_json(&self) -> Json {
        Json::Object(btreemap!{
            "level".to_string() => self.level.to_json(),
            "constant".to_string() => self.constant.to_json(),
            "variable".to_string() => self.variable.to_json()
        })
    } 
}



