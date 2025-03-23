package laba4;

import java.util.*;

public class A {
    static int[] a;
    static int[] b;
    static int n, m;

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        n = sc.nextInt();
        m = sc.nextInt();

        a = new int[n];
        b = new int[m];

        for (int i = 0; i < n; i++) {
            a[i] = sc.nextInt();
        }

        for (int i = 0; i < m; i++) {
            b[i] = sc.nextInt();
        }

        Arrays.sort(a);

        for (int j = 0; j < m; j++) {
            int count = binarySearch(a, b[j]);
            System.out.print(count + " ");
        }
    }

    static int binarySearch(int[] a, int value) {
        int l = 0;
        int r = a.length - 1;
        int res = 0;

        while (l <= r) {
            int mid = l + (r - l) / 2;
            if (a[mid] <= value) {
                res = mid + 1;
                l = mid + 1;
            } else {
                r = mid - 1;
            }
        }

        return res;
    }
}