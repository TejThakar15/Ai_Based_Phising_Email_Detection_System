import java.util.*;

class Main {
    public static void main(String args[]) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        ArrayList<Integer> squares = new ArrayList<>();
        int totalSum = 0;

        for (int i = 0; i < n; i++) {
            int score = sc.nextInt();
            if (score >= 0) {
                int root = (int) Math.sqrt(score);
                if (root * root == score) {
                    squares.add(score);
                    totalSum += score;
                }
            }
        }

        if (squares.size() > 0) {
            System.out.print("Perfect square scores : ");
            for (int i = 0; i < squares.size(); i++) {
                System.out.print(squares.get(i));
                if (i < squares.size() - 1) {
                    System.out.print(" ");
                }
            }
            System.out.println();
            System.out.println("Total incentive score : " + totalSum);

        } else {
            System.out.println("Perfect square scores : None");
            System.out.println("No eligible batches found. ");
        }
    }
}